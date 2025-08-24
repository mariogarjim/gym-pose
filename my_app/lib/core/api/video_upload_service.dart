// lib/core/api/video_upload_service.dart

import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

typedef Progress = void Function(int sent, int total);

class VideoUploadService {
  
  static String get _baseUrl => kDebugMode 
    ? 'https://6ox7wiysef.execute-api.eu-west-1.amazonaws.com/prod'
    : 'https://api.gym-pose.com/api/v1/video/upload';

  static Future<Map<String, String>> getPresignedUrl({required String exerciseType, required String userId}) async {
    print('Url: $_baseUrl');
    final uri = Uri.parse('$_baseUrl/generate-presigned-url').replace(queryParameters: {
      'exercise_type': exerciseType,
      'user_id': userId,
      'filename': 'video.mp4',
    });

    final response = await http.post(uri);

    print('Response: ${response}');

    if (response.statusCode != 200) {
      throw Exception('HTTP request failed: ${response.statusCode} - ${response.body}');
    }

    final responseBody = jsonDecode(response.body);
    print('Response body: $responseBody');
    
    final url = responseBody['url'] as String;
    print('Url: $url');
    final key = responseBody['key'] as String;
    print('Key: $key');

    return {
      'url': url,
      'key': key,
    };
  }

  static Future<void> uploadVideoWithProgress({
    required Uri presignedUrl,
    required File file,
    String contentType = 'video/mp4',
    Progress? onProgress,
  }) async {
      final client = http.Client();
      try {
        final length = await file.length();
        final stream = file.openRead();
        int sent = 0;

        final request = http.StreamedRequest('PUT', presignedUrl)
          ..headers['Content-Type'] = contentType
          ..headers['Content-Length'] = length.toString();

        await for (final chunk in stream) {
          request.sink.add(chunk);
          sent += chunk.length;
          onProgress?.call(sent, length);
        }
        await request.sink.close();

        final response = await client.send(request);
        if (response.statusCode != 200 && response.statusCode != 204) {
          final body = await response.stream.bytesToString();
          throw Exception('Upload failed: ${response.statusCode} — $body');
        }
        else {
          print('Upload successful');
        }
      } finally {
        client.close();
      }
  }
}
