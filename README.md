# gif.py
Attempt to create a gif decoder


## decoder
- [x] Header
- [x] Logical Screen Descriptor
- [x] Global Color Table
- [x] Extentions:
- - [x] Graphic Control Extension
- - [x] Comment Extension
- - [x] Plain Text Extension
- - [x] Application Extension
- [x] Image Descriptor
- [x] Local Color Table
- [ ] Image Data

## viewer
- [x] Global Color Table
- [x] Local Color Table of first image
- [ ] First image
- [x] Local Color Table of other images
- [ ] Other images
- [ ] Animation
- [ ] Transparency
- [ ] Disposal Methods
- [ ] Text rendering by Plain Text Extension


## Usage
```shell
.\gif.py sample.gif
```
It will create `gif_data.js` that include decoded color table and index stream of image  
To view decoded color table and image open `viewer.html`


## References
GIF specification [GIF87a](https://www.w3.org/Graphics/GIF/spec-gif87.txt)  
GIF specification [GIF89a](https://www.w3.org/Graphics/GIF/spec-gif89a.txt)  
[3MF Project: What's In A GIF - Bit by Byte](https://www.matthewflickinger.com/lab/whatsinagif/)