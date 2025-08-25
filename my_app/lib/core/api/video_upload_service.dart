// lib/core/api/video_upload_service.dart

import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:my_app/constants.dart';
import 'package:my_app/core/utils/zip_utils.dart';


typedef Progress = void Function(int sent, int total);

const baseUrl = 'https://6ox7wiysef.execute-api.eu-west-1.amazonaws.com/prod';

class VideoUploadService {

  static Future<Map<String, String>> getPresignedUrlForZip({required String exerciseType, required String userId}) async {
    final mappedExerciseType = mappingExerciseTypeToSlotId[exerciseType];
    if (mappedExerciseType == null) {
      throw Exception('Invalid exercise type: $exerciseType');
    }
    
    // Get presigned url for zip file
    final uri = Uri.parse('$baseUrl/generate-presigned-url').replace(queryParameters: {
      'exercise_type': mappedExerciseType,
      'user_id': userId,
      'filename': 'data.zip',
    });
    final response = await http.post(uri);

    if (response.statusCode != 200) {
      throw Exception('HTTP request failed: ${response.statusCode} - ${response.body}');
    }

    final responseBody = jsonDecode(response.body);

    return {
      'url': responseBody['url'] as String,
      'key': responseBody['key'] as String,
    };
  }

  static Future<void> uploadZipWithProgress({
    required Uri presignedUrl,
    required Map<String, File> files,
    required String zipFileName,
    String contentType = 'application/zip',
    Progress? onProgress,
  }) async {
    File? zipFile;
    final client = http.Client();
    
    try {
      // Create zip file from the provided files
      zipFile = await ZipUtils.createZipFromFilesWithNames(
        filesMap: files,
        zipFileName: zipFileName,
      );

      final length = await zipFile.length();
      final stream = zipFile.openRead();

      final request = http.StreamedRequest('PUT', presignedUrl)
        ..contentLength = length;

      // Ensure headers match what was signed
      final signedHeadersCsv = presignedUrl.queryParameters['X-Amz-SignedHeaders'];
      final signedHeaders = signedHeadersCsv?.split(';') ?? const <String>[];
      if (signedHeaders.contains('content-type')) {
        request.headers['Content-Type'] = contentType;
      }
      if (signedHeaders.contains('x-amz-content-sha256')) {
        request.headers['x-amz-content-sha256'] = 'UNSIGNED-PAYLOAD';
      }

      // Send the zip file to the presigned url
      int sent = 0;
      await for (final chunk in stream) {
        request.sink.add(chunk);
        sent += chunk.length;
        onProgress?.call(sent, length);
      }

      // Close the request
      request.sink.close();

      // Send the request
      final response = await client.send(request);
      
      // Check if the upload was successful
      if (response.statusCode != 200) {
        final body = await response.stream.bytesToString();
        throw Exception('Upload failed: ${response.statusCode} — $body');
      }
      
    } finally {
      client.close();
      
      // Clean up the temporary zip file
      if (zipFile != null) {
        await ZipUtils.cleanupZipFile(zipFile);
      }
    }
  }
}
