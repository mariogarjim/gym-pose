// lib/core/api/video_upload_service.dart

import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:my_app/core/utils/mime_utils.dart';

class VideoUploadService {
  static const String _uploadUrl = 'http://10.0.2.2:8000/api/v1/video/upload';

  static Future<List<int>> uploadVideo(File videoFile) async {
    final request = http.MultipartRequest('POST', Uri.parse(_uploadUrl));

    final multipartFile = await http.MultipartFile.fromPath(
      'file',
      videoFile.path,
      contentType: getMimeType(videoFile.path),
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
