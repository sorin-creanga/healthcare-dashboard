import com.sun.net.httpserver.*;
import java.io.*;
import java.net.InetSocketAddress;
import java.util.*;
import java.time.LocalDateTime;

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
        
        // Home page
        server.createContext("/", exchange -> {
            String html = "<html><body style='font-family:Arial; padding:20px'>" +
                "<h1>Healthcare ED Dashboard API</h1>" +
                "<p>Your API is running successfully!</p>" +
                "<h3>Try these endpoints:</h3>" +
                "<ul>" +
                "<li><a href='/api/health'>Health Check</a></li>" +
                "<li><a href='/api/metrics'>ED Metrics</a></li>" +
                "<li><a href='/api/patients'>View Patients</a></li>" +
                "</ul>" +
                "<p style='color:green'>Server Status: RUNNING</p>" +
                "<p>Time: " + LocalDateTime.now() + "</p>" +
                "</body></html>";
            
            exchange.getResponseHeaders().set("Content-Type", "text/html");
            exchange.sendResponseHeaders(200, html.getBytes().length);
            OutputStream os = exchange.getResponseBody();
            os.write(html.getBytes());
            os.close();
        });
        
        // Health check endpoint
        server.createContext("/api/health", exchange -> {
            String json = "{" +
                "\"status\":\"UP\"," +
                "\"message\":\"Healthcare API is healthy\"," +
                "\"timestamp\":\"" + LocalDateTime.now() + "\"" +
                "}";
            
            sendJsonResponse(exchange, json);
            System.out.println("Health check performed");
        });
        
        // Metrics endpoint
        server.createContext("/api/metrics", exchange -> {
            int waiting = 0;
            int inTreatment = 0;
            double totalWait = 0;
            
            for (Map<String, Object> p : patients) {
                String status = (String) p.get("status");
                if (status.equals("WAITING")) waiting++;
                if (status.equals("IN_TREATMENT")) inTreatment++;
                totalWait += (Integer) p.get("waitTime");
            }
            
            double avgWait = patients.size() > 0 ? totalWait / patients.size() : 0;
            String saturation = patients.size() > 20 ? "RED" : 
                               patients.size() > 10 ? "YELLOW" : "GREEN";
            
            String json = "{" +
                "\"totalPatients\":" + patients.size() + "," +
                "\"waitingPatients\":" + waiting + "," +
                "\"inTreatment\":" + inTreatment + "," +
                "\"averageWaitTime\":" + String.format("%.1f", avgWait) + "," +
                "\"saturationLevel\":\"" + saturation + "\"," +
                "\"timestamp\":\"" + LocalDateTime.now() + "\"" +
                "}";
            
            sendJsonResponse(exchange, json);
            System.out.println("Metrics requested - Total patients: " + patients.size());
        });
        
        // Patients endpoint
        server.createContext("/api/patients", exchange -> {
            StringBuilder json = new StringBuilder("[");
            for (int i = 0; i < patients.size(); i++) {
                if (i > 0) json.append(",");
                Map<String, Object> p = patients.get(i);
                json.append("{");
                json.append("\"id\":").append(p.get("id")).append(",");
                json.append("\"anonymousId\":\"").append(p.get("anonymousId")).append("\",");
                json.append("\"complaint\":\"").append(p.get("complaint")).append("\",");
                json.append("\"triage\":\"").append(p.get("triage")).append("\",");
                json.append("\"status\":\"").append(p.get("status")).append("\",");
                json.append("\"waitTime\":").append(p.get("waitTime"));
                json.append("}");
            }
            json.append("]");
            
            sendJsonResponse(exchange, json.toString());
            System.out.println("Patient list requested");
        });
        
        // Start the server
        server.start();
        
        System.out.println("========================================");
        System.out.println("SERVER IS RUNNING SUCCESSFULLY!");
        System.out.println("========================================");
        System.out.println("Open your browser and go to:");
        System.out.println("   http://localhost:8080");
        System.out.println("========================================");
        System.out.println("Press Ctrl+C to stop the server");
    }
    
    // Helper method to send JSON responses
    static void sendJsonResponse(HttpExchange exchange, String json) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        exchange.sendResponseHeaders(200, json.getBytes().length);
        OutputStream os = exchange.getResponseBody();
        os.write(json.getBytes());
        os.close();
    }
    
    // Add sample patients
    static void addSamplePatients() {
        String[] complaints = {"Chest Pain", "Fever", "Broken Arm", "Headache", "Breathing Issues"};
        String[] triages = {"CRITICAL", "URGENT", "URGENT", "STANDARD", "CRITICAL"};
        String[] statuses = {"IN_TREATMENT", "WAITING", "WAITING", "DISCHARGED", "IN_TREATMENT"};
        int[] waitTimes = {5, 45, 30, 120, 10};
        
        for (int i = 0; i < 5; i++) {
            Map<String, Object> patient = new HashMap<>();
            patient.put("id", patientIdCounter++);
            patient.put("anonymousId", "PT-2024-" + String.format("%03d", i + 1));
            patient.put("complaint", complaints[i]);
            patient.put("triage", triages[i]);
            patient.put("status", statuses[i]);
            patient.put("waitTime", waitTimes[i]);
            patients.add(patient);
        }
        System.out.println("Added " + patients.size() + " sample patients");
    }
}