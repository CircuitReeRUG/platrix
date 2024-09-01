Monitor
---

Requires node 22+.

Records pixel matrix changes through websocket.


Generate images
---

Written in python. 

Requires Pillow.

From the recorded pixel matrix changes generates an image sequence.

To compose a video from the generated images you can use ffmpeg:
Notice the framerate parameter below is set to 6fps.

```
ffmpeg -y -hide_banner -pattern_type glob -framerate 6 -i 'images/*.png' -vf scale="-1:1080:flags=neighbor" -pix_fmt yuv420p pixel-timelapse.mp4
```
