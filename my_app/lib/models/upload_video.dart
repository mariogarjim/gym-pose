class UploadVideoResult {
  final List<int> zipBytes;
  final String feedback;
  final int clipsGenerated;

  UploadVideoResult({
    required this.zipBytes,
    required this.feedback,
    required this.clipsGenerated,
  });
}