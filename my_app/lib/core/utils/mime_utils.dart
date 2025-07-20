import 'package:http_parser/http_parser.dart';
import 'package:path/path.dart' as path;

MediaType getMimeType(String filePath) {
  final ext = path.extension(filePath).toLowerCase();
  switch (ext) {
    case '.mp4':
      return MediaType('video', 'mp4');
    default:
      throw Exception('Unsupported file extension: $ext');
  }
}