// lib/core/api/video_upload_service.dart

import 'package:http/http.dart' as http;
import 'package:my_app/core/utils/mime_utils.dart';
import 'package:my_app/models/upload_video.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import 'dart:typed_data';
import 'package:archive/archive.dart';

class VideoUploadService {
  
  static const String _baseUrl = 'http://10.0.2.2:8000/api/v1/video/upload';

  static Future<UploadVideoResult> uploadAndProcessVideo({required String videoPath, required String exerciseType}) async {
    final uri = Uri.parse(_baseUrl).replace(queryParameters: {
      'exercise_type': exerciseType,
    });

    final request = http.MultipartRequest('POST', uri);

    final multipartFile = await http.MultipartFile.fromPath(
      'file',
      videoPath,
      contentType: getMimeType(videoPath),
    );

    request.files.add(multipartFile);

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      throw Exception('Upload failed: ${response.body}');
    }

    final feedback = response.headers['x-exercise-feedback'];
    final clipsGenerated = response.headers['x-clips-generated'];
    final zipBytes = response.bodyBytes;
    final extractedDirectory = await _extractZip(zipBytes);

    final int clipsGeneratedInt = int.parse(clipsGenerated ?? '0');

    return UploadVideoResult(
      zipBytes: zipBytes,
      feedback: feedback ?? '',
      clipsGenerated: clipsGeneratedInt,
      extractedDirectory: extractedDirectory,
    );
  }

  static Future<Directory> _extractZip(Uint8List zipBytes) async {
    final archive = ZipDecoder().decodeBytes(zipBytes);

    final appDocDir = await getApplicationDocumentsDirectory();
    final outputDir = Directory(path.join(appDocDir.path, "unzipped_videos_${DateTime.now().millisecondsSinceEpoch}"));
    outputDir.createSync(recursive: true);

    for (final file in archive) {
      final filePath = path.join(outputDir.path, file.name);

      if (file.isFile) {
        final outFile = File(filePath);
        await outFile.create(recursive: true);
        await outFile.writeAsBytes(file.content as List<int>);
      }
    }

    return outputDir;
  }
}
