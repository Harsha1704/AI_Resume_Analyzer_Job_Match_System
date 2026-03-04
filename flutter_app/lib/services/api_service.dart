import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = "http://10.0.2.2:5000"; 
  // Change to laptop IP if using real device

  static Future<Map<String, dynamic>> analyzeResume(String resumeText) async {
    final response = await http.post(
      Uri.parse("$baseUrl/analyze"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"resume": resumeText}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to analyze resume");
    }
  }
}