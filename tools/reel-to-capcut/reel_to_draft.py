"""
reel_to_draft.py
================
The6ixToSauga / Sierra Brook / JL Fitness — Reel Script → CapCut Draft Generator

Usage:
    python reel_to_draft.py <script.json> --drafts-folder "/path/to/CapCut Drafts"

The script.json format is documented in reel_schema.json.
Run with --example to generate a sample script file you can edit.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import pycapcut as cc
from pycapcut import (
    SEC, trange, tim,
    TrackType, FontType, TextStyle, ClipSettings,
    IntroType, OutroType, TransitionType,
    VideoSceneEffectType, FilterType,
    TextIntro, TextOutro,
    TextBackground,
)

# ─────────────────────────────────────────────────────────────
# BRAND PROFILES
# ─────────────────────────────────────────────────────────────

BRANDS = {
    "the6ixtosauga": {
        "label":       "The6ixToSauga",
        "width":       1080,
        "height":      1920,
        "fps":         30,
        "font":        FontType.Anton,
        "text_color":  (1.0, 1.0, 1.0),
        "text_size":   9.0,
        "text_bold":   True,
        "text_y":      -0.72,            # bottom-third
        "text_intro":  TextIntro.故障,
        "text_outro":  TextOutro.渐隐,
        "filter":      FilterType.Gritty_Noir,
        "filter_int":  60.0,
        "clip_effect": VideoSceneEffectType.Ghosting,
        "transition":  TransitionType.Snap_Zoom,
        "hook_transition": TransitionType.Flash,
    },
    "sierrabrook": {
        "label":       "Sierra Brook",
        "width":       1080,
        "height":      1920,
        "fps":         30,
        "font":        FontType.ALEGREYA,
        "text_color":  (1.0, 0.98, 0.92),
        "text_size":   7.5,
        "text_bold":   False,
        "text_y":      -0.72,
        "text_intro":  TextIntro.渐显,
        "text_outro":  TextOutro.渐隐,
        "filter":      FilterType.Candlelight,
        "filter_int":  55.0,
        "clip_effect": VideoSceneEffectType.Dreamy_Halo,
        "transition":  TransitionType.Dreamy_Bubbles,
        "hook_transition": TransitionType.Light_Leaks,
    },
    "jlfitness": {
        "label":       "JL Fitness / Operation Apex",
        "width":       1080,
        "height":      1920,
        "fps":         30,
        "font":        FontType.Anton,
        "text_color":  (0.784, 0.957, 0.0),   # electric chartreuse #c8f400
        "text_size":   9.0,
        "text_bold":   True,
        "text_y":      -0.72,
        "text_intro":  TextIntro.故障,          # glitch snap-in — matches the hard-cut energy
        "text_outro":  TextOutro.渐隐,
        "filter":      FilterType.Gritty_Noir,
        "filter_int":  65.0,
        "clip_effect": VideoSceneEffectType.Ghosting,
        "transition":  TransitionType.Snap_Zoom,
        "hook_transition": TransitionType.Flash,
    },
}


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def sec(s: float) -> int:
    """Convert float seconds to microseconds."""
    return int(s * SEC)


def resolve_brand(raw: str) -> dict:
    key = raw.lower().replace(" ", "").replace("_", "").replace("-", "")
    for k, v in BRANDS.items():
        if k in key or key in k:
            return v
    raise ValueError(
        f"Unknown brand '{raw}'. Use 'the6ixtosauga', 'sierrabrook', or 'jlfitness'."
    )


def resolve_asset(path: str, base_dir: str) -> str:
    """Resolve asset path: absolute, relative to script dir, or placeholder."""
    if path.startswith("PLACEHOLDER"):
        return path          # caller must handle missing files
    p = Path(path)
    if p.is_absolute() and p.exists():
        return str(p)
    rel = Path(base_dir) / path
    if rel.exists():
        return str(rel)
    raise FileNotFoundError(
        f"Asset not found: '{path}'\n"
        f"  Tried absolute: {p}\n"
        f"  Tried relative to script dir: {rel}\n"
        "  Update the path in your JSON, or use a PLACEHOLDER_ prefix to skip."
    )


# ─────────────────────────────────────────────────────────────
# CORE BUILDER
# ─────────────────────────────────────────────────────────────

def build_draft(data: dict, drafts_folder: str, base_dir: str, overwrite: bool = False) -> None:

    # ── Meta ──────────────────────────────────────────────────
    draft_name  = data.get("draft_name", "Reel Draft")
    brand_cfg   = resolve_brand(data.get("brand", "the6ixtosauga"))
    W, H        = brand_cfg["width"], brand_cfg["height"]
    FPS         = brand_cfg["fps"]
    clips       = data.get("clips", [])
    audio_path  = data.get("audio_path", "")
    audio_vol   = float(data.get("audio_volume", 0.35))
    add_filter  = data.get("apply_filter", True)
    add_fx      = data.get("apply_effects", True)
    overwrite   = data.get("overwrite", False)

    overwrite   = overwrite or data.get("overwrite", False)

    print(f"\n{'─'*56}")
    print(f"  Brand     : {brand_cfg['label']}")
    print(f"  Draft     : {draft_name}")
    print(f"  Canvas    : {W}×{H}  {FPS}fps")
    print(f"  Clips     : {len(clips)}")
    print(f"{'─'*56}\n")

    # ── Create draft ──────────────────────────────────────────
    folder = cc.DraftFolder(drafts_folder)
    script = folder.create_draft(draft_name, W, H, fps=FPS, allow_replace=overwrite)

    # ── Tracks ────────────────────────────────────────────────
    script.add_track(TrackType.video,  "main_video",  relative_index=1)
    script.add_track(TrackType.text,   "captions",    relative_index=1)
    script.add_track(TrackType.audio,  "music",       relative_index=1)
    script.add_track(TrackType.effect, "fx_track",    relative_index=1)
    script.add_track(TrackType.filter, "filter_track",relative_index=1)

    # ── Cursor tracking ───────────────────────────────────────
    cursor_us = 0                # current timeline position in µs
    total_clips = len(clips)

    # ── Build clips ───────────────────────────────────────────
    for i, clip in enumerate(clips):
        is_hook    = clip.get("section", "body") == "hook"
        duration_s = float(clip.get("duration", 3.0))
        dur_us     = sec(duration_s)
        asset_raw  = clip.get("asset", "")
        caption    = clip.get("caption", "")
        vo_text    = clip.get("voiceover", "")
        clip_label = clip.get("label", f"Clip {i+1}")

        print(f"  [{i+1:02d}/{total_clips}] {clip_label}  ({duration_s}s)  ", end="")

        # ── Video segment ─────────────────────────────────────
        if asset_raw and not asset_raw.startswith("PLACEHOLDER"):
            try:
                asset_path = resolve_asset(asset_raw, base_dir)
                vseg = cc.VideoSegment(
                    asset_path,
                    trange(cursor_us, dur_us),
                    volume=0.0,                    # mute — music track handles audio
                    clip_settings=ClipSettings(
                        scale_x=1.0,
                        scale_y=1.0,
                    ),
                )

                # ── Transition (not on first clip) ────────────
                if i > 0:
                    t_type = (
                        brand_cfg["hook_transition"]
                        if is_hook else brand_cfg["transition"]
                    )
                    vseg.add_transition(t_type, duration="0.4s")

                # ── Clip-level effect (hook clips only for 6ixToSauga) ─
                if add_fx and is_hook:
                    vseg.add_effect(brand_cfg["clip_effect"])

                script.add_segment(vseg, "main_video")
                print("✓ video", end="")

            except FileNotFoundError as e:
                print(f"\n    ⚠ SKIPPED (asset not found): {e}")
        else:
            print("– no asset (skipped)", end="")

        # ── Caption / on-screen text ──────────────────────────
        display_text = caption or vo_text
        if display_text:
            txt_style = TextStyle(
                size      = brand_cfg["text_size"],
                bold      = brand_cfg["text_bold"],
                color     = brand_cfg["text_color"],
                auto_wrapping  = True,
                max_line_width = 0.78,
            )
            txt_seg = cc.TextSegment(
                display_text,
                trange(cursor_us, dur_us),
                font   = brand_cfg["font"],
                style  = txt_style,
                clip_settings = ClipSettings(transform_y=brand_cfg["text_y"]),
            )
            txt_seg.add_animation(brand_cfg["text_intro"])
            txt_seg.add_animation(brand_cfg["text_outro"])
            script.add_segment(txt_seg, "captions")
            print("  ✓ caption", end="")

        print()
        cursor_us += dur_us

    total_duration_us = cursor_us

    # ── Global filter (whole timeline) ────────────────────────
    if add_filter:
        script.add_filter(
            brand_cfg["filter"],
            trange(0, total_duration_us),
            track_name = "filter_track",
            intensity  = brand_cfg["filter_int"],
        )
        print(f"\n  ✓ Filter applied: {brand_cfg['filter'].name}  ({brand_cfg['filter_int']:.0f}%)")

    # ── Music track ───────────────────────────────────────────
    if audio_path and not audio_path.startswith("PLACEHOLDER"):
        try:
            audio_file = resolve_asset(audio_path, base_dir)
            # Trim or loop to match total duration
            audio_mat  = cc.AudioMaterial(audio_file)
            src_dur    = audio_mat.duration
            use_dur    = min(src_dur, total_duration_us)

            aseg = cc.AudioSegment(
                audio_mat,
                trange(0, use_dur),
                source_timerange = trange(0, use_dur),
                volume           = audio_vol,
            )
            script.add_segment(aseg, "music")
            print(f"  ✓ Music: {Path(audio_file).name}  (vol {audio_vol*100:.0f}%)")

        except FileNotFoundError as e:
            print(f"  ⚠ Music skipped: {e}")
    else:
        print("  – No music path provided (add one later in CapCut)")

    # ── Save ──────────────────────────────────────────────────
    script.save()
    total_s = total_duration_us / SEC
    print(f"\n  ✅ Draft saved: '{draft_name}'")
    print(f"     Total duration: {total_s:.1f}s")
    print(f"     Open CapCut → refresh drafts list to find it.\n")


# ─────────────────────────────────────────────────────────────
# EXAMPLE JSON GENERATOR
# ─────────────────────────────────────────────────────────────

EXAMPLE_SCRIPT = {
    "_comment": "The6ixToSauga Reel Script — replace PLACEHOLDER_ paths with real files",
    "draft_name":      "The6ixToSauga — 3 Mistakes Buyers Make",
    "brand":           "the6ixtosauga",
    "audio_path":      "PLACEHOLDER_music.mp3",
    "audio_volume":    0.30,
    "apply_filter":    True,
    "apply_effects":   True,
    "clips": [
        {
            "label":     "Hook — Scroll-stop",
            "section":   "hook",
            "duration":  2.5,
            "asset":     "PLACEHOLDER_hook_broll.mp4",
            "caption":   "3 mistakes GTA buyers make in 2025 🚨",
            "voiceover": "If you're buying in the GTA right now, you need to hear this."
        },
        {
            "label":     "Hook — Stakes",
            "section":   "hook",
            "duration":  2.5,
            "asset":     "PLACEHOLDER_city_wide.mp4",
            "caption":   "Mistake #1",
            "voiceover": "Skipping the pre-approval."
        },
        {
            "label":     "Value — Point 1",
            "section":   "body",
            "duration":  4.0,
            "asset":     "PLACEHOLDER_consult.mp4",
            "caption":   "Without a pre-approval, sellers won't look at your offer.",
            "voiceover": "In this market, sellers don't even consider offers without a solid pre-approval letter."
        },
        {
            "label":     "Value — Point 2 intro",
            "section":   "body",
            "duration":  2.5,
            "asset":     "PLACEHOLDER_neighbourhood.mp4",
            "caption":   "Mistake #2",
            "voiceover": "Buying in the wrong neighbourhood for your lifestyle."
        },
        {
            "label":     "Value — Point 2 detail",
            "section":   "body",
            "duration":  4.0,
            "asset":     "PLACEHOLDER_street.mp4",
            "caption":   "Mississauga ≠ Etobicoke ≠ Downtown. They're different worlds.",
            "voiceover": "The difference between Mississauga, Etobicoke, and Downtown isn't just geography — it's lifestyle."
        },
        {
            "label":     "Value — Point 3 intro",
            "section":   "body",
            "duration":  2.5,
            "asset":     "PLACEHOLDER_paperwork.mp4",
            "caption":   "Mistake #3",
            "voiceover": "Waiving the home inspection."
        },
        {
            "label":     "Value — Point 3 detail",
            "section":   "body",
            "duration":  4.0,
            "asset":     "PLACEHOLDER_inspection.mp4",
            "caption":   "It feels like a winning move. It's not.",
            "voiceover": "I know waiving inspection feels like it gives you an edge — but the risk is not worth it."
        },
        {
            "label":     "CTA",
            "section":   "cta",
            "duration":  3.0,
            "asset":     "PLACEHOLDER_talking_head_cta.mp4",
            "caption":   "DM me MAP for your free buyer guide 📩",
            "voiceover": "DM me the word MAP and I'll send you your free GTA buyer guide."
        }
    ]
}

EXAMPLE_SCRIPT_SIERRA = {
    "_comment": "Sierra Brook Reel Script — replace PLACEHOLDER_ paths with real files",
    "draft_name":      "Sierra Brook — Signs Your Parent Needs Help",
    "brand":           "sierrabrook",
    "audio_path":      "PLACEHOLDER_gentle_music.mp3",
    "audio_volume":    0.25,
    "apply_filter":    True,
    "apply_effects":   False,
    "clips": [
        {
            "label":     "Hook",
            "section":   "hook",
            "duration":  3.5,
            "asset":     "PLACEHOLDER_senior_at_window.mp4",
            "caption":   "5 signs your parent may need in-home support",
            "voiceover": "Sometimes the hardest part is knowing when it's time to ask for help."
        },
        {
            "label":     "Sign 1",
            "section":   "body",
            "duration":  4.0,
            "asset":     "PLACEHOLDER_kitchen_scene.mp4",
            "caption":   "Missed meals or unexplained weight loss",
            "voiceover": "If you're noticing missed meals or changes in weight, that's a signal."
        },
        {
            "label":     "Sign 2",
            "section":   "body",
            "duration":  4.0,
            "asset":     "PLACEHOLDER_caregiver_walking.mp4",
            "caption":   "Difficulty with everyday tasks",
            "voiceover": "Trouble with bathing, dressing, or getting around the home safely."
        },
        {
            "label":     "Sign 3",
            "section":   "body",
            "duration":  4.0,
            "asset":     "PLACEHOLDER_family_conversation.mp4",
            "caption":   "Increased isolation or loneliness",
            "voiceover": "Social withdrawal can be just as serious as a physical symptom."
        },
        {
            "label":     "CTA",
            "section":   "cta",
            "duration":  4.0,
            "asset":     "PLACEHOLDER_caregiver_smile.mp4",
            "caption":   "Love Doesn't Forget. We're here. 💛",
            "voiceover": "At Sierra Brook, we're here to help your family take that next step with dignity."
        }
    ]
}


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert a Reel script JSON into a CapCut draft.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "script",
        nargs="?",
        help="Path to your reel_script.json file.",
    )
    parser.add_argument(
        "--drafts-folder", "-d",
        required=False,
        help='Path to your CapCut Drafts folder, e.g. "C:/Users/You/CapCut Drafts"',
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Write example JSON files to the current directory and exit.",
    )
    parser.add_argument(
        "--brand",
        choices=["the6ixtosauga", "sierrabrook", "jlfitness"],
        help="Override the brand in the JSON.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing draft with the same name.",
    )
    args = parser.parse_args()

    # ── Write example files ───────────────────────────────────
    if args.example:
        out_6ix   = Path("reel_script_6ix.json")
        out_sb    = Path("reel_script_sierra.json")
        out_6ix.write_text(json.dumps(EXAMPLE_SCRIPT,        indent=2, ensure_ascii=False))
        out_sb.write_text( json.dumps(EXAMPLE_SCRIPT_SIERRA, indent=2, ensure_ascii=False))
        print(f"✅ Example scripts written:")
        print(f"   {out_6ix.resolve()}")
        print(f"   {out_sb.resolve()}")
        print("\nEdit the files, swap PLACEHOLDER_ paths for real assets,")
        print("then run:\n")
        print('  python reel_to_draft.py reel_script_6ix.json --drafts-folder "YOUR_DRAFTS_PATH"')
        sys.exit(0)

    # ── Validate args ─────────────────────────────────────────
    if not args.script:
        parser.print_help()
        sys.exit(1)

    if not args.drafts_folder:
        print("❌  --drafts-folder is required.")
        print('    Example: --drafts-folder "C:/Users/Abraham/CapCut Drafts"')
        sys.exit(1)

    script_path = Path(args.script)
    if not script_path.exists():
        print(f"❌  Script file not found: {script_path}")
        sys.exit(1)

    drafts_folder = args.drafts_folder
    if not Path(drafts_folder).exists():
        print(f"❌  Drafts folder not found: {drafts_folder}")
        print("    Open CapCut → Global Settings → Draft Location to find the correct path.")
        sys.exit(1)

    # ── Load and (optionally) override ───────────────────────
    data = json.loads(script_path.read_text(encoding="utf-8"))
    if args.brand:
        data["brand"] = args.brand

    base_dir = str(script_path.parent.resolve())

    # ── Build ─────────────────────────────────────────────────
    build_draft(data, drafts_folder, base_dir, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
