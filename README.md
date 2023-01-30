
# rm_anime_bg

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Python Versions](https://img.shields.io/badge/python-3.9%20%7C%203.10-blue)
[![CI](https://github.com/shirayu/rm_anime_bg/actions/workflows/ci.yml/badge.svg)](https://github.com/shirayu/rm_anime_bg/actions/workflows/ci.yml)
[![CodeQL](https://github.com/shirayu/rm_anime_bg/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/shirayu/rm_anime_bg/actions/workflows/codeql-analysis.yml)
[![Typos](https://github.com/shirayu/rm_anime_bg/actions/workflows/typos.yml/badge.svg)](https://github.com/shirayu/rm_anime_bg/actions/workflows/typos.yml)

A simple CLI of anime background remover with [SkyTNT/anime-segmentation](https://github.com/SkyTNT/anime-segmentation)

![An example of input image](example/example_0_original.png)
![An example of output image](example/example_0_after.png)

[Image source](https://ja.wikipedia.org/wiki/%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB:Wikipe-tan_meets_mathematics.png), licensed under CC-BY-SA-3.0, Funa Funa

## Setup

```bash
pip install -U git+https://github.com/shirayu/rm_anime_bg.git@v0.0.0
```

## Usage

```bash
rm_anime_bg -o [Output directory] [Input 1] [Input 2]
```

Run ``rm_anime_bg --help`` for full command options

### Example

```bash
rm_anime_bg -o /path/to/output_dir input1.png input2.png
```

## Links

- <https://github.com/SkyTNT/anime-segmentation>

## License

Apache License 2.0
