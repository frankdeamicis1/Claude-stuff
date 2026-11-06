# PC build story: voiceover script + captions

60 s, 1080×1920, for Reels and TikTok. You build a gaming PC start to finish:
plan, buy, build, stress test, hand it to a happy customer. Then the CTA:
"In San Diego? DM me."

## Which file to use

- `out/pc-build-story.mp4`: **record over this one.** Read-along captions + quiet music + sound effects.
- `out/pc-build-story-sfx-only.mp4`: same read-along captions, sound effects only (add a trending sound).
- `out/pc-build-story-clean.mp4`: no captions, if you'd rather use the app's auto-captions after recording.

## How to record so it lines up

You don't need to memorize anything or watch a clock. The video tells you what to say and when:

1. **The word you should be saying lights up yellow.** Captions show each phrase a moment before you say it. Just read along.
2. **The hook, "I handle it", and the ending have no captions.** The big text pops up on the exact word instead, so read it as it appears: "powerful"… "reliable"… "fits your budget".
3. Start talking right away: the first word is at 0:00.4.
4. Do one practice run with the sound on, then record.

**Easier still: record one step at a time.** Instagram, TikTok and CapCut all let you stop and restart the voiceover. Each line starts right when its step starts (times below), so if you mess one up, redo just that line.

The lines are short on purpose: about 2 words a second with real pauses, slower than the last video.

| Starts | On screen | You say |
|---|---|---|
| 0:00 | "You want a gaming PC that's" Powerful / Reliable / Fits your budget | You want a gaming PC that's powerful, reliable, and fits your budget. |
| 0:06 | "I handle it. Start to finish." | I handle it. Start to finish. |
| 0:10 | Step 1 PLAN: budget, games, monitor → budget bar | Step one. Your budget, your games, your monitor. I plan the build around that. |
| 0:18 | Step 2 BUY: phone order, boxes land, "Works together" | Step two. I buy the parts and make sure they all work together. |
| 0:26 | Step 3 BUILD: parts click in, cables cleaned up, lights on | Step three. I build it clean. Every part seated right, cables cleaned up. |
| 0:35 | Step 4 STRESS TEST: full load → "All tests passed" | Step four. I stress test it. If something's going to fail, it fails on my bench, not at your house. |
| 0:45 | Step 5 IT'S YOURS: customer, thumbs up, confetti | Step five. It's yours. Plug it in and play. |
| 0:52 | IN SAN DIEGO? → DM ME → your budget + what you play | In San Diego? DM me your budget and what you play. I'll tell you what I'd build. |

### Sound

- The background audio is mixed quiet on purpose: about -30 LUFS overall, every hit capped at -12 dBFS. A normal speaking voice is around -16 to -14 LUFS, so you sit about 10 dB or more on top.
- Leave the video's original sound at 100% and talk at your normal volume, with the phone about a hand's width from your mouth.
- If you still sound buried, turn the original sound down to about 70% rather than pushing your voice up.

## Instagram caption

The first line shows before "more", so the CTA goes there.

```
In San Diego and want a gaming PC that's powerful, reliable, and actually in your budget? DM me.

Here's how it works, start to finish:
1. Plan it around your budget, your games, and your monitor
2. Buy the parts and make sure they all work together
3. Build it clean
4. Stress test it at full load. If something's going to fail, it fails on my bench, not at your house.
5. Hand it off. You plug it in and play.

DM me your budget and what you play, and I'll tell you what I'd build.

#sandiego #gamingpc #pcbuild #custompc #pcgaming
```

Set the post's location tag to San Diego so it gets shown to people nearby.

## TikTok caption

```
In San Diego? DM me your budget and what you play. I'll plan it, build it, stress test it, and hand it off ready to play.

#sandiego #gamingpc #pcbuild #custompc
```

Check that your TikTok message settings let people who don't follow you send you a DM.

## DM reply

> Hey, appreciate you reaching out. A few quick questions so I can point you the right way: what's your budget, what games do you play, and what part of San Diego are you in? If you know your monitor (1080p, 1440p, 4K, refresh rate), send that too. I'll tell you what I'd build for it.

## Notes

- The budget bar in step 1 is an example split (graphics card biggest, then CPU, then board/RAM/SSD, then power supply/case). It has no dollar amounts on purpose.
- The temps in the stress test (around 70 °C CPU, 65 °C GPU) are illustrative, not from a real build.
- The customer is a cartoon, not a real person, and there's no quote or review in their mouth.
- To change a line, edit `VO` in `story.html` (each line's start time + text). The captions, word timing and on-screen pops all follow it. Then run `./build.sh`.
