"""
Example Usage: Working with Pipeline Output
This script shows how to programmatically use the pipeline output
"""

import json
from pathlib import Path

# ============================================================================
# EXAMPLE 1: Load and inspect transcript metadata
# ============================================================================

def load_transcript_metadata():
    """Load the transcript metadata JSON file."""
    metadata_file = Path("output/transcript_metadata.json")
    
    if not metadata_file.exists():
        print("Metadata file not found. Run main.py first.")
        return None
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    return metadata


def print_meeting_summary(metadata):
    """Print summary of the meeting."""
    print("\n" + "="*70)
    print("MEETING SUMMARY")
    print("="*70)
    
    duration = metadata["duration_seconds"]
    minutes = int(duration) // 60
    seconds = int(duration) % 60
    
    print(f"Number of speakers:    {metadata['num_speakers']}")
    print(f"Number of segments:    {metadata['num_segments']}")
    print(f"Meeting duration:      {minutes}:{seconds:02d}")
    print(f"Device used:           {metadata['device']}")
    
    print(f"\nSpeaker mapping:")
    for speaker_id, speaker_label in sorted(metadata["speaker_mapping"].items()):
        speaker_num = speaker_id.split("_")[-1]
        print(f"  {speaker_id} → {speaker_label}")
    
    print("="*70 + "\n")


# ============================================================================
# EXAMPLE 2: Filter segments by speaker
# ============================================================================

def get_speaker_segments(metadata, speaker_label):
    """Get all segments from a specific speaker."""
    segments = metadata["segments"]
    speaker_segments = [s for s in segments if s.get("speaker_label") == speaker_label]
    return speaker_segments


def print_speaker_transcript(metadata, speaker_label):
    """Print transcript for a specific speaker."""
    segments = get_speaker_segments(metadata, speaker_label)
    
    if not segments:
        print(f"No segments found for {speaker_label}")
        return
    
    print(f"\n{speaker_label}'s Speech:")
    print("-" * 70)
    
    for seg in segments:
        timestamp = f"[{int(seg['start']):02d}:{int(seg['start']%60):02d}]"
        text = seg["text"]
        confidence = seg.get("overlap_confidence", 0)
        print(f"{timestamp} (confidence: {confidence:.1%}) {text}")
    
    print("-" * 70)


# ============================================================================
# EXAMPLE 3: Extract by time range
# ============================================================================

def get_segments_by_time(metadata, start_seconds, end_seconds):
    """Get segments within a specific time range."""
    segments = metadata["segments"]
    result = [
        s for s in segments
        if s["start"] >= start_seconds and s["end"] <= end_seconds
    ]
    return result


def print_time_range_transcript(metadata, start_seconds, end_seconds):
    """Print transcript for a time range."""
    segments = get_segments_by_time(metadata, start_seconds, end_seconds)
    
    if not segments:
        print(f"No segments found in [{start_seconds}s, {end_seconds}s]")
        return
    
    start_min = int(start_seconds) // 60
    start_sec = int(start_seconds) % 60
    end_min = int(end_seconds) // 60
    end_sec = int(end_seconds) % 60
    
    print(f"\nTranscript [{start_min}:{start_sec:02d} - {end_min}:{end_sec:02d}]:")
    print("-" * 70)
    
    for seg in segments:
        timestamp = f"[{int(seg['start']):02d}:{int(seg['start']%60):02d}]"
        speaker = seg.get("speaker_label", "Unknown")
        text = seg["text"]
        print(f"{timestamp} {speaker}: {text}")
    
    print("-" * 70)


# ============================================================================
# EXAMPLE 4: Speaker statistics
# ============================================================================

def analyze_speaker_statistics(metadata):
    """Analyze speech statistics per speaker."""
    segments = metadata["segments"]
    
    stats = {}
    for seg in segments:
        speaker = seg.get("speaker_label", "Unknown")
        if speaker not in stats:
            stats[speaker] = {
                "count": 0,
                "duration": 0,
                "words": 0,
                "avg_confidence": 0
            }
        
        stats[speaker]["count"] += 1
        stats[speaker]["duration"] += seg["end"] - seg["start"]
        stats[speaker]["words"] += len(seg["text"].split())
        stats[speaker]["avg_confidence"] += seg.get("overlap_confidence", 0)
    
    # Calculate averages
    for speaker in stats:
        if stats[speaker]["count"] > 0:
            stats[speaker]["avg_confidence"] /= stats[speaker]["count"]
    
    return stats


def print_speaker_statistics(metadata):
    """Print detailed speaker statistics."""
    stats = analyze_speaker_statistics(metadata)
    
    print("\n" + "="*70)
    print("SPEAKER STATISTICS")
    print("="*70)
    
    for speaker, data in sorted(stats.items()):
        duration_min = int(data["duration"]) // 60
        duration_sec = int(data["duration"]) % 60
        
        print(f"\n{speaker}:")
        print(f"  Speech segments:      {data['count']}")
        print(f"  Total duration:       {duration_min}:{duration_sec:02d}")
        print(f"  Average segment:      {data['duration']/data['count']:.1f}s")
        print(f"  Word count:           {data['words']}")
        print(f"  Avg confidence:       {data['avg_confidence']:.1%}")
        
        if data["duration"] > 0:
            wpm = (data["words"] / data["duration"]) * 60
            print(f"  Speaking rate:        {wpm:.0f} words/minute")
    
    print("="*70)


# ============================================================================
# EXAMPLE 5: Export to different formats
# ============================================================================

def export_to_csv(metadata):
    """Export transcript to CSV format."""
    import csv
    
    output_file = Path("output/transcript.csv")
    segments = metadata["segments"]
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "speaker", "text", "duration", "confidence"]
        )
        writer.writeheader()
        
        for seg in segments:
            duration = seg["end"] - seg["start"]
            writer.writerow({
                "timestamp": f"{int(seg['start']):02d}:{int(seg['start']%60):02d}",
                "speaker": seg.get("speaker_label", "Unknown"),
                "text": seg["text"],
                "duration": f"{duration:.2f}",
                "confidence": f"{seg.get('overlap_confidence', 0):.2%}"
            })
    
    print(f"✓ Exported to: {output_file}")


def export_to_srt(metadata):
    """Export transcript to SRT (subtitle) format."""
    output_file = Path("output/transcript.srt")
    segments = metadata["segments"]
    
    def seconds_to_timestamp(seconds):
        hours = int(seconds) // 3600
        minutes = (int(seconds) % 3600) // 60
        secs = int(seconds) % 60
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    with open(output_file, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, 1):
            speaker = seg.get("speaker_label", "Unknown")
            text = seg["text"]
            
            f.write(f"{idx}\n")
            f.write(f"{seconds_to_timestamp(seg['start'])} --> {seconds_to_timestamp(seg['end'])}\n")
            f.write(f"{speaker}: {text}\n\n")
    
    print(f"✓ Exported to: {output_file}")


# ============================================================================
# EXAMPLE 6: Search functionality
# ============================================================================

def search_transcript(metadata, keywords):
    """Search for keywords in transcript."""
    segments = metadata["segments"]
    results = []
    
    for seg in segments:
        text = seg["text"].lower()
        for keyword in keywords:
            if keyword.lower() in text:
                results.append(seg)
                break
    
    return results


def print_search_results(metadata, keywords):
    """Print search results."""
    results = search_transcript(metadata, keywords)
    
    if not results:
        print(f"No segments found containing: {keywords}")
        return
    
    print(f"\nSearch results for: {keywords}")
    print("-" * 70)
    
    for seg in results:
        timestamp = f"[{int(seg['start']):02d}:{int(seg['start']%60):02d}]"
        speaker = seg.get("speaker_label", "Unknown")
        text = seg["text"]
        
        # Highlight keywords
        highlighted = text
        for keyword in keywords:
            highlighted = highlighted.replace(
                keyword,
                f">>> {keyword} <<<",
                1
            )
        
        print(f"{timestamp} {speaker}: {highlighted}")
    
    print("-" * 70)


# ============================================================================
# EXAMPLE 7: Generate meeting minutes
# ============================================================================

def generate_meeting_minutes(metadata):
    """Generate a summary-style meeting minutes format."""
    stats = analyze_speaker_statistics(metadata)
    segments = metadata["segments"]
    
    output = []
    output.append("="*70)
    output.append("MEETING MINUTES")
    output.append("="*70)
    output.append("")
    
    # Attendees
    output.append("ATTENDEES:")
    for speaker in sorted(stats.keys()):
        output.append(f"  • {speaker}")
    output.append("")
    
    # Duration
    duration = metadata["duration_seconds"]
    minutes = int(duration) // 60
    seconds = int(duration) % 60
    output.append(f"DURATION: {minutes}:{seconds:02d}")
    output.append("")
    
    # Transcript
    output.append("DISCUSSION:")
    for seg in segments:
        speaker = seg.get("speaker_label", "Unknown")
        text = seg["text"]
        output.append(f"{speaker}: {text}")
    
    output.append("")
    output.append("="*70)
    
    return "\n".join(output)


# ============================================================================
# MAIN EXAMPLE
# ============================================================================

def main():
    """Run all examples."""
    print("Speaker Diarization Pipeline - Usage Examples")
    
    # Load metadata
    metadata = load_transcript_metadata()
    if metadata is None:
        return
    
    # Example 1: Print summary
    print_meeting_summary(metadata)
    
    # Example 2: Speaker-specific transcript
    first_speaker = list(metadata["speaker_mapping"].values())[0]
    print_speaker_transcript(metadata, first_speaker)
    
    # Example 3: Time-range transcript
    if metadata["duration_seconds"] > 60:
        print_time_range_transcript(metadata, 0, min(60, metadata["duration_seconds"]))
    
    # Example 4: Speaker statistics
    print_speaker_statistics(metadata)
    
    # Example 5: Export formats
    try:
        export_to_csv(metadata)
        export_to_srt(metadata)
    except Exception as e:
        print(f"Export failed: {e}")
    
    # Example 6: Search
    keywords = ["meeting", "discuss", "need"]
    print_search_results(metadata, keywords)
    
    # Example 7: Meeting minutes
    minutes = generate_meeting_minutes(metadata)
    with open("output/meeting_minutes.txt", "w", encoding="utf-8") as f:
        f.write(minutes)
    print("\n✓ Generated meeting_minutes.txt")


if __name__ == "__main__":
    main()
