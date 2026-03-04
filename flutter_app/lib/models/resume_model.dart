class ResumeResult {
  final String predictedRole;
  final double atsScore;
  final List<String> skillGap;

  ResumeResult({
    required this.predictedRole,
    required this.atsScore,
    required this.skillGap,
  });

  factory ResumeResult.fromJson(Map<String, dynamic> json) {
    return ResumeResult(
      predictedRole: json['predicted_role'],
      atsScore: json['ats_score'].toDouble(),
      skillGap: List<String>.from(json['skill_gap']),
    );
  }
}