// lib/core/utils/zip_utils.dart

import 'dart:io';
import 'package:archive/archive.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

class ZipUtils {
  /// Creates a zip file from a list of files
  /// Returns the path to the created zip file
  static Future<File> createZipFromFiles({
    required List<File> files,
    required String zipFileName,
  }) async {
    final archive = Archive();

    // Add each file to the archive
    for (final file in files) {
      if (await file.exists()) {
        final bytes = await file.readAsBytes();
        final fileName = path.basename(file.path);
        
        final archiveFile = ArchiveFile(fileName, bytes.length, bytes);
        archive.addFile(archiveFile);
      }
    }

    // Encode the archive to zip format
    final zipData = ZipEncoder().encode(archive);
    if (zipData == null) {
      throw Exception('Failed to create zip file');
    }

    // Get temporary directory to save the zip file
    final tempDir = await getTemporaryDirectory();
    final zipFile = File(path.join(tempDir.path, zipFileName));

    // Write the zip data to file
    await zipFile.writeAsBytes(zipData);

    return zipFile;
  }

  /// Creates a zip file with custom file names from a map of files
  /// Map key is the desired filename in the zip, value is the File
  static Future<File> createZipFromFilesWithNames({
    required Map<String, File> filesMap,
    required String zipFileName,
  }) async {
    final archive = Archive();

    // Add each file to the archive with custom names
    for (final entry in filesMap.entries) {
      final customName = entry.key;
      final file = entry.value;
      
      if (await file.exists()) {
        final bytes = await file.readAsBytes();
        
        final archiveFile = ArchiveFile(customName, bytes.length, bytes);
        archive.addFile(archiveFile);
      }
    }

    // Encode the archive to zip format
    final zipData = ZipEncoder().encode(archive);
    if (zipData == null) {
      throw Exception('Failed to create zip file');
    }

    // Get temporary directory to save the zip file
    final tempDir = await getTemporaryDirectory();
    final zipFile = File(path.join(tempDir.path, zipFileName));

    // Write the zip data to file
    await zipFile.writeAsBytes(zipData);

    return zipFile;
  }

  /// Cleans up temporary zip files
  static Future<void> cleanupZipFile(File zipFile) async {
    try {
      if (await zipFile.exists()) {
        await zipFile.delete();
      }
    } catch (e) {
      print('Error cleaning up zip file: $e');
    }
  }
}
