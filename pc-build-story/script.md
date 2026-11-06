# PC build story: voiceover script + captions

59 s, 1080×1920. You build a gaming PC start to finish: plan, buy, build,
stress test, hand it to a happy customer. Then the CTA: "In San Diego? DM me."

Two versions:

- `out/pc-build-story.mp4`: soft music bed + sound effects, mixed quiet (about -30 LUFS) so your voice sits on top
- `out/pc-build-story-sfx-only.mp4`: sound effects only, if you'd rather add a trending sound

## Voiceover (word for word)

The tracker at the top shows which step you're on, so you don't have to hit
the exact second. Just start each line when its step comes up.

| Time | On screen | You say |
|---|---|---|
| 0:00 | "You want a gaming PC that's" Powerful / Reliable / In your budget | You want a gaming PC that's actually powerful, doesn't crash on you, and fits your budget. |
| 0:06 | "I handle it. Start to finish." + the 5 steps | That's what I do. Here's how it works, start to finish. |
| 0:10 | 1 PLAN: budget, games, monitor → budget bar | First, you tell me your budget, the games you play, and your monitor. I plan the whole build around that. |
| 0:18 | 2 BUY: parts list fills up, boxes land, "Works together" | Then I buy the parts and make sure they all work together. I'm going for value, not the flashiest box. |
| 0:26 | 3 BUILD: parts click in, cables cleaned up, lights on | Then I build it. Every part seated right, cables cleaned up, and it actually looks good when the lights come on. |
| 0:35 | 4 STRESS TEST: CPU, GPU, memory at full load → "All tests passed" | Then I stress test it. Full load, watching the temps. If something's going to fail, it fails on my bench, not at your house. |
| 0:44 | 5 IT'S YOURS: customer, thumbs up, confetti | Then it's yours. Plug it in and play. That's it. |
| 0:51 | "Want one built for your budget? In San Diego? DM me" | In San Diego? Want one built for your budget? DM me your budget and what you play. |

### Recording tips

- The background audio is mixed quiet on purpose: about -30 LUFS overall, with every hit capped at -12 dBFS. A normal speaking voice is around -16 to -14 LUFS, so you sit about 10 dB or more on top.
- Leave the video's original sound at 100% and record at your normal volume, with the phone about a hand's width from your mouth.
- If your voice still sounds buried (phone far away, quiet delivery), turn the original sound down to about 70%. That works better than pushing your voice up.
- If you add auto-captions, drag them down over the workbench. The top half already has the on-screen text.

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
- The temps in the stress test (around 70 °C CPU, 66 °C GPU) are illustrative, not from a real build.
- The customer is a cartoon, not a real person, and there's no quote or review in their mouth.
- To change any text, edit `story.html` and run `./build.sh`.
