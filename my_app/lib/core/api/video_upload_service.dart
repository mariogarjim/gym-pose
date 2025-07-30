// lib/core/api/video_upload_service.dart

import 'package:http/http.dart' as http;
import 'package:my_app/core/utils/mime_utils.dart';

class VideoUploadService {
  static const String _baseUrl = 'http://10.0.2.2:8000/api/v1/video/upload';

  static Future<List<int>> uploadAndProcessVideo({required String videoPath, required String exerciseType}) async {
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

    return response.bodyBytes;
  }
}
