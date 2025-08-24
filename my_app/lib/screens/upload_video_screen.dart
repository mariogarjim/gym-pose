import 'dart:typed_data';
import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:video_thumbnail/video_thumbnail.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:my_app/theme/text_styles.dart';
import 'package:my_app/screens/feedback_exercise_selection_screen.dart';
import 'package:my_app/app_shell.dart';
import 'package:my_app/core/api/video_upload_service.dart';

final requiredVideos = {
  "SQUATS": [
    {"id": "side", "label": "Side View", "description": "Film from your left or right side"},
  ],
  "PULL-UPS": [
    {"id": "back", "label": "Back View", "description": "Film yourself from the back"},
  ],
  "LATERAL RAISES": [
    {"id": "front", "label": "Front View", "description": "Film yourself facing the camera"},
  ],
};


// Reusable upload card (same look as before)
class MediaTile extends StatelessWidget {
  const MediaTile({
    super.key,
    required this.thumbnail,
    required this.onPickFromGallery,
    required this.onPickFromCamera,
    this.onRemove,
    this.size = 120,
  });

  final Uint8List? thumbnail;
  final VoidCallback onPickFromGallery;
  final VoidCallback onPickFromCamera;
  final VoidCallback? onRemove;
  final double size;

  @override
  Widget build(BuildContext context) {
    final hasMedia = thumbnail != null;

    return Stack(
      clipBehavior: Clip.none,
      children: [
        GestureDetector(
          onTap: onPickFromGallery,
          onLongPress: onPickFromCamera,
          child: 
        ClipRRect(
          borderRadius: BorderRadius.circular(14),
          child: Container(
            width: size,
            height: size,
            color: hasMedia ? Colors.black12 : const Color(0xFFE5E7EB),
            child: hasMedia
                ? Image.memory(thumbnail!, fit: BoxFit.cover)
                : Center(
                    child: Container(
                      width: 36, height: 36,
                      decoration: const BoxDecoration(shape: BoxShape.circle, color: Colors.white70),
                      child: const Icon(Icons.add, size: 22, color: Colors.black87),
                    ),
                  ),
          ),
        ),
        ),
        if (hasMedia && onRemove != null)
          Positioned(
            top: -6, right: -6,
            child: InkWell(
              onTap: onRemove,
              borderRadius: BorderRadius.circular(16),
              child: Container(
                width: 28, height: 28,
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: const Color(0x33000000)),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.close, size: 16),
              ),
            ),
          ),
        Positioned(
          bottom: -8, left: -8,
            child: Container(
              width: 38, height: 38,
              decoration: const BoxDecoration(
                color: Colors.white, shape: BoxShape.circle,
                boxShadow: [BoxShadow(blurRadius: 8, offset: Offset(0,2), color: Color(0x1A000000))]
              ),
              child: const Icon(Icons.video_call, size: 22),
            ),
          ),
      ],
    );
  }
}

/// Screen that adapts to `requiredVideos[exerciseName]`
class UploadRequiredVideosScreen extends StatefulWidget {
  const UploadRequiredVideosScreen({
    super.key,
    required this.exerciseName,
  });

  final String exerciseName;

  @override
  State<UploadRequiredVideosScreen> createState() => _UploadRequiredVideosScreenState();
}

class _UploadRequiredVideosScreenState extends State<UploadRequiredVideosScreen> {
  final ImagePicker _picker = ImagePicker();

  late final List<Map<String, String>> _requirements;
  late final String _exerciseName;

  // slotId -> file/thumb
  final Map<String, XFile?> _files = {};
  final Map<String, Uint8List?> _thumbs = {};

  bool get _readyToContinue =>
      _requirements.isNotEmpty &&
      _requirements.every((r) => _thumbs[r['id']] != null);

  Future<void> _handlePermissionRequest() async {
    final videoPermissions = await Permission.videos.isGranted;
    final imagePermissions = await Permission.photos.isGranted;
    if (!videoPermissions || !imagePermissions) {
      await Permission.videos.request();
      await Permission.photos.request();
    }
  }

  @override
  void initState() {
    super.initState();
    _handlePermissionRequest();

    _exerciseName = widget.exerciseName;
    final list = requiredVideos[_exerciseName] ?? const [];
    _requirements = List<Map<String, String>>.from(list);
    for (final r in _requirements) {
      _files[r['id']!] = null;
      _thumbs[r['id']!] = null;
    }
  }

  Future<void> _pickVideo({
    required String slotId,
    required ImageSource source,
  }) async {
    try {
      final file = await _picker.pickVideo(source: source, maxDuration: const Duration(minutes: 2));
      if (file == null) return;

      final thumb = await VideoThumbnail.thumbnailData(
        video: file.path,
        imageFormat: ImageFormat.JPEG,
        maxWidth: 480,
        quality: 75,
      );

      if (!mounted) return;
      setState(() {
        _files[slotId] = file;
        _thumbs[slotId] = thumb;
      });
    } catch (e) {
      debugPrint('Pick video error ($slotId): $e');
    }
  }

  void _remove(String slotId) {
    setState(() {
      _files[slotId] = null;
      _thumbs[slotId] = null;
    });
  }

  @override
Widget build(BuildContext context) {

  return Scaffold(
    // 👇 main scrollable content
    body: SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 80), // bottom padding so button doesn’t overlap
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.only(left: 12, right: 16),
            child: Text(
              'Upload your videos',
              style: AppTextStylesV2.screenTitle,
            ),
          ),
          const SizedBox(height: 30),

          // Your video slots
          ..._requirements.map((req) {
            final slotId = req['id']!;
            final label = req['label']!;
            final desc = req['description']!;

            return Padding(
              padding: const EdgeInsets.only(bottom: 30, left: 16, right: 16),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  MediaTile(
                    thumbnail: _thumbs[slotId],
                    onPickFromGallery: () => _pickVideo(slotId: slotId, source: ImageSource.gallery),
                    onPickFromCamera: () => _pickVideo(slotId: slotId, source: ImageSource.camera),
                    onRemove: _thumbs[slotId] != null ? () => _remove(slotId) : null,
                    size: 120,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 6),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(label, style: AppTextStylesV2.requirementLabel),
                          const SizedBox(height: 6),
                          Text(desc, style: AppTextStylesV2.requirementDescription),
                          const SizedBox(height: 8),
                          Text(
                            'Tap to choose • Long-press for camera',
                            style: AppTextStylesV2.requirementHint,
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),

          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              'Please, ensure your whole body is visible. Thank you :)',
              style: AppTextStylesV2.textBody,
            ),
          ),
        ],
      ),
    ),

    // 👇 fixed continue button
   bottomNavigationBar: SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(32, 0, 32, 16),
        child: SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.black,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
            onPressed: _readyToContinue
            ? () async {
                    for (final file in _files.values) {
                      if (file == null) continue;
                      final presignedUrl = await VideoUploadService.getPresignedUrl(exerciseType: _exerciseName, userId: 'user1234');
                      print('Presigned URL: ${presignedUrl['url']}');
                      VideoUploadService.uploadVideoWithProgress(
                        presignedUrl: Uri.parse(presignedUrl['url']!),
                        file: File(file.path),
                      onProgress: (sent, total) {
                        print('Upload progress: $sent/$total');
                      },
                      );
                      final shell = AppShell.of(context);
                      // ✅ push inside tab 2 so the navbar stays and AppShell is the ancestor
                      shell?.pushOnTab(
                        2,
                        MaterialPageRoute(
                          builder: (_) => FeedbackExerciseSelectionsScreen(exerciseName: _exerciseName),
                        ),
                    );
                  }
                }
                : null,
            child: const Text(
              "Continue",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
          ),
        ),
      ),
    ),
  );
}

}


