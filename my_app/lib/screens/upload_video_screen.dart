import 'dart:typed_data';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:video_thumbnail/video_thumbnail.dart';

final requiredVideos = {
  "SQUATS": [
    {"id": "side", "label": "Side View", "description": "Film from your left or right side"},
    {"id": "front", "label": "Front View", "description": "Film yourself facing the camera"},
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
          child: GestureDetector(
            onTap: onPickFromGallery,
            onLongPress: onPickFromCamera,
            child: Container(
              width: 38, height: 38,
              decoration: const BoxDecoration(
                color: Colors.white, shape: BoxShape.circle,
                boxShadow: [BoxShadow(blurRadius: 8, offset: Offset(0,2), color: Color(0x1A000000))]
              ),
              child: const Icon(Icons.video_call, size: 22),
            ),
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

  // slotId -> file/thumb
  final Map<String, XFile?> _files = {};
  final Map<String, Uint8List?> _thumbs = {};

  bool get _readyToContinue =>
      _requirements.isNotEmpty &&
      _requirements.every((r) => _thumbs[r['id']] != null);

  @override
  void initState() {
    super.initState();
    final list = requiredVideos[widget.exerciseName] ?? const [];
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
    final t = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new),
          onPressed: () => Navigator.of(context).maybePop(),
        ),
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1),
          child: Divider(height: 1, thickness: 1, color: Color(0xFFE0E0E0)),
        ),
      ),
      backgroundColor: Colors.white,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              'Upload your videos',
              style: t.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
            ),
          ),
          const SizedBox(height: 8),

          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
              itemCount: _requirements.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, i) {
                final req = _requirements[i];
                final slotId = req['id']!;
                final label = req['label']!;
                final desc  = req['description']!;

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
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
                                Text(label, style: t.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                                const SizedBox(height: 6),
                                Text(desc, style: t.textTheme.bodyMedium),
                                const SizedBox(height: 8),
                                Text(
                                  'Tap to choose • Long-press for camera',
                                  style: t.textTheme.bodySmall?.copyWith(color: Colors.grey[600]),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                );
              },
            ),
          ),

          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16),
            child: Text('Please, ensure your whole body is visible. Thank you :)'),
          ),
          const SizedBox(height: 8),

          // Continue button appears only when all required slots are filled
          SafeArea(
            top: false,
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 250),
              child: _readyToContinue
                  ? Padding(
                      padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                      child: SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: () {
                            // Access picked files by slotId
                            // Example: _files['side'] / _files['front'] / _files['back']
                            debugPrint('Continue for ${widget.exerciseName}: ${_files.map((k, v) => MapEntry(k, v?.path))}');
                            // TODO: navigate / upload
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.black,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                          child: const Text('Continue', style: TextStyle(fontWeight: FontWeight.w600)),
                        ),
                      ),
                    )
                  : const SizedBox.shrink(),
            ),
          ),
        ],
      ),
    );
  }
}
