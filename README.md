# DendroTweaks

<img src="https://dendrotweaks.readthedocs.io/en/latest/_static/logo.png" width="25%">
<p>

**DendroTweaks** is a Python toolbox designed for creating and validating single-cell biophysical models with active dendrites. 

It is available both as a standalone Python package and a web-based application.

## Learn More

- **Standalone Library**: Explore the [official documentation](https://dendrotweaks.readthedocs.io/en/latest/index.html) for detailed tutorials and API reference.
- **Web Application**: Access the GUI online via our platform at [dendrotweaks.dendrites.gr](https://dendrotweaks.dendrites.gr).
- **Quick Overview**: Check out our [e-poster](https://doi.org/10.57736/abba-7149), including a video demonstration, presented at the FENS Forum 2024 in Vienna.
- **Latest News**: Follow us on [Bluesky](https://bsky.app/profile/dendrotweaks.bsky.social) for updates.

## Publication

For an in-depth understanding of DendroTweaks, refer to our publication in *eLife*:

> Roman Makarov, Spyridon Chavlis, Panayiota Poirazi (2025).  
> *DendroTweaks, an interactive approach for unraveling dendritic dynamics.*  
> eLife 13:RP103324. [https://doi.org/10.7554/eLife.103324.3](https://doi.org/10.7554/eLife.103324.3)

If you find DendroTweaks helpful for your research, please consider citing our work:

```bibtex
@article {Makarov2025,
    article_type = {journal},
    title = {DendroTweaks, an interactive approach for unraveling dendritic dynamics},
    author = {Makarov, Roman and Chavlis, Spyridon and Poirazi, Panayiota},
    volume = 13,
    year = 2025,
    month = {dec},
    pub_date = {2025-12-23},
    pages = {RP103324},
    citation = {eLife 2025;13:RP103324},
    doi = {10.7554/eLife.103324},
    url = {https://doi.org/10.7554/eLife.103324},
    journal = {eLife},
    issn = {2050-084X},
    publisher = {eLife Sciences Publications, Ltd},
}
```

## License

This project uses multiple licenses depending on the content:

- **Library code (`src/dendrotweaks/*.py`)**: Mozilla Public License 2.0 (MPL-2.0).  
  All modifications to these files must remain under MPL-2.0 when redistributed.

- **Documentation (`docs/`)**: Creative Commons Attribution 4.0 (CC-BY-4.0).  
  You are free to copy, modify, and distribute the documentation, with attribution.

- **Examples (`examples/`)**: no formal license; provided for demonstration purposes.  
  Use freely in your own projects.

- **Templates (`src/dendrotweaks/biophys/default_templates`)**: no formal license (permissive). You may reuse, modify, or include them in your projects freely.

- **Third-party or model files (`*.mod`)**: license may vary or be unknown; see individual files.

> **Note:** Previous versions of this project (before version 0.5.0) were released under GPL-3.0. This relicensing applies to releases from v0.5.0 onward.
