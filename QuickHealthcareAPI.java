import com.sun.net.httpserver.*;
import java.io.*;
import java.net.InetSocketAddress;
import java.util.*;
import java.time.LocalDateTime;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

public class QuickHealthcareAPI {
    
    // Store our patients data
    static List<Map<String, Object>> patients = new ArrayList<>();
    static int patientIdCounter = 1;
    
    public static void main(String[] args) throws Exception {
        System.out.println("Starting Healthcare Dashboard API...");
        
        // Add some sample patients
        addSamplePatients();
        
        // Create server on port 8080
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        
        // 1. DASHBOARD ENDPOINT (Root)
        server.createContext("/", exchange -> {
            StringBuilder html = new StringBuilder();
            
            // HTML Header with 30-Second Meta Refresh
            html.append("<html><head>")
                .append("<meta http-equiv='refresh' content='30'>") // <--- FIXED: Now 30 seconds
                .append("<title>ED Dashboard</title>")
                .append("<style>")
                .append("body { font-family: sans-serif; padding: 20px; background: #f0f2f5; }")
                .append(".card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }")
                .append("table { width: 100%; border-collapse: collapse; }")
                .append("th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }")
                .append(".CRITICAL { color: #d32f2f; font-weight: bold; }")
                .append(".URGENT { color: #f57c00; font-weight: bold; }")
                .append("</style>")
                .append("</head><body>");

            // Calculate Metrics 
            int waiting = 0;
            for (Map<String, Object> p : patients) {
                if ("WAITING".equals(p.get("status"))) waiting++;
            }

            // Build UI
            html.append("<h1> Hospital ED Dashboard</h1>");
            
            html.append("<div class='card'>");
            html.append("<h2>Current Status</h2>");
            html.append("<p>Total Patients: <b>").append(patients.size()).append("</b></p>");
            html.append("<p>Waiting Room: <b>").append(waiting).append("</b></p>");
            html.append("<p>Last Updated: ").append(LocalDateTime.now()).append("</p>");
            html.append("</div>");

            html.append("<div class='card'>");
            html.append("<h2>Patient Queue</h2>");
            html.append("<table>");
            html.append("<tr><th>ID</th><th>Triage</th><th>Complaint</th><th>Status</th><th>Wait Time</th></tr>");

            // Show most recent patients first
            List<Map<String, Object>> reversedList = new ArrayList<>(patients);
            Collections.reverse(reversedList);

            for (Map<String, Object> p : reversedList) {
                String triageClass = (String) p.get("triage");
                html.append("<tr>");
                html.append("<td>").append(p.get("anonymousId")).append("</td>");
                html.append("<td class='").append(triageClass).append("'>").append(p.get("triage")).append("</td>");
                html.append("<td>").append(p.get("complaint")).append("</td>");
                html.append("<td>").append(p.get("status")).append("</td>");
                html.append("<td>").append(p.get("waitTime")).append(" min</td>");
                html.append("</tr>");
            }

            html.append("</table></div>");
            html.append("</body></html>");

            byte[] responseBytes = html.toString().getBytes();
            exchange.getResponseHeaders().set("Content-Type", "text/html");
            exchange.sendResponseHeaders(200, responseBytes.length);
            OutputStream os = exchange.getResponseBody();
            os.write(responseBytes);
            os.close();
        });
        
        // 2. METRICS API (For checking data raw)
        server.createContext("/api/metrics", exchange -> {
            int waiting = 0;
            for (Map<String, Object> p : patients) {
                if ("WAITING".equals(p.get("status"))) waiting++;
            }
            String json = "{\"totalPatients\":" + patients.size() + ", \"waitingPatients\":" + waiting + "}";
            sendJsonResponse(exchange, json);
        });
        
        // 3. PATIENTS API (Handles GET list AND Python POST data)
        server.createContext("/api/patients", exchange -> {
            
            // >>> THIS IS THE NEW PART YOU MISSED <<<
            // Handle POST requests (Incoming data from Python)
            if ("POST".equals(exchange.getRequestMethod())) {
                try {
                    // Parse the Query Parameters sent by Python
                    String query = exchange.getRequestURI().getQuery();
                    Map<String, String> params = parseQuery(query);

                    // Create new patient object
                    Map<String, Object> newPatient = new HashMap<>();
                    newPatient.put("id", patientIdCounter++);
                    newPatient.put("anonymousId", "PT-NEW-" + (1000 + new Random().nextInt(9000)));
                    
                    // Map Python keys (chiefComplaint) to Java keys (complaint)
                    newPatient.put("complaint", params.getOrDefault("chiefComplaint", "Unknown"));
                    newPatient.put("triage", params.getOrDefault("triageLevel", "STANDARD"));
                    newPatient.put("status", "WAITING");
                    newPatient.put("waitTime", 0); // Just arrived

                    // Add to database
                    patients.add(newPatient);
                    System.out.println("✅ Received new patient from Python: " + newPatient.get("complaint"));

                    sendJsonResponse(exchange, "{\"message\": \"Patient Added\"}");
                } catch (Exception e) {
                    e.printStackTrace();
                    exchange.sendResponseHeaders(500, 0);
                    exchange.close();
                }
                return;
            }
            
            // Handle GET requests (View list JSON)
            StringBuilder json = new StringBuilder("[");
            for (int i = 0; i < patients.size(); i++) {
                if (i > 0) json.append(",");
                Map<String, Object> p = patients.get(i);
                json.append("{");
                json.append("\"id\":").append(p.get("id")).append(",");
                json.append("\"anonymousId\":\"").append(p.get("anonymousId")).append("\",");
                json.append("\"complaint\":\"").append(p.get("complaint")).append("\",");
                json.append("\"triage\":\"").append(p.get("triage")).append("\"");
                json.append("}");
            }
            json.append("]");
            sendJsonResponse(exchange, json.toString());
        });
        
        server.start();
        System.out.println("Server started on http://localhost:8080");
    }
    
    // Helper to send JSON
    static void sendJsonResponse(HttpExchange exchange, String json) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        exchange.sendResponseHeaders(200, json.getBytes().length);
        OutputStream os = exchange.getResponseBody();
        os.write(json.getBytes());
        os.close();
    }

    // Helper to parse URL parameters from Python
    static Map<String, String> parseQuery(String query) {
        Map<String, String> result = new HashMap<>();
        if (query == null) return result;
        for (String param : query.split("&")) {
            String[] entry = param.split("=");
            if (entry.length > 1) {
                result.put(entry[0], URLDecoder.decode(entry[1], StandardCharsets.UTF_8));
            } else {
                result.put(entry[0], "");
            }
        }
        return result;
    }

    static void addSamplePatients() {
        // Initial dummy data
        Map<String, Object> p = new HashMap<>();
        p.put("id", patientIdCounter++);
        p.put("anonymousId", "PT-INIT-001");
        p.put("complaint", "Initial Test Patient");
        p.put("triage", "STANDARD");
        p.put("status", "WAITING");
        p.put("waitTime", 10);
        patients.add(p);
    }
}