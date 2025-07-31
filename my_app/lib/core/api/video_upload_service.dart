// lib/core/api/video_upload_service.dart

import 'package:http/http.dart' as http;
import 'package:my_app/core/utils/mime_utils.dart';
import 'package:my_app/models/upload_video.dart';

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


    final int clipsGeneratedInt = int.parse(clipsGenerated ?? '0');

    return UploadVideoResult(
      zipBytes: response.bodyBytes,
      feedback: feedback ?? '',
      clipsGenerated: clipsGeneratedInt,
    );
  }
}
