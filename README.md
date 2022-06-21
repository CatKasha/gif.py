# gif.py
Attempt to create a gif decoder

## Usage
```
gif.py path_to_gif
```
It will create `gif_data.js` that include decoded color table and index stream of image  
To view decoded color table and image open `index.html`

## TODO
- ~~Local Color Table~~
- Parse all extensions
- - ~~Graphic Control Extension~~
- - ~~Comment Extension~~
- - ~~Plain Text Extension~~
- - Application Extension
- Animation and Transparency
- Implement text rendering by Plain Text Extension
- Gif viewer using Tkinter
- ...
- Rewrite everything in C

## References
GIF specification [GIF87a](https://www.w3.org/Graphics/GIF/spec-gif87.txt)  
GIF specification [GIF89a](https://www.w3.org/Graphics/GIF/spec-gif89a.txt)  
[What's In A GIF](https://www.matthewflickinger.com/lab/whatsinagif/)  
^ great guide that take you through GIF89a spec and explain everything, including LZW algorithm