import 'dart:typed_data';
import 'dart:io';

class UploadVideoResult {
  final Uint8List zipBytes;
  final String feedback;
  final int clipsGenerated;
  final Directory extractedDirectory;

  UploadVideoResult({
    required this.zipBytes,
    required this.feedback,
    required this.clipsGenerated,
    required this.extractedDirectory,
  });
}