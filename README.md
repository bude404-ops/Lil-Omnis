Lil Omnis

A multichain collection of tiny mysteries.

Lil Omnis is a cute, collectible character project built around interconnected blockchains, hidden knowledge, cryptic symbols, riddles, and six separate chapters of a larger mystery.

The project begins with layered character artwork and NFT generation, with future plans for a lore archive, interactive discoveries, and optional game integrations.

Project Goals

- Create a consistent, recognizable Lil Omni character design.
- Build a modular artwork system using interchangeable layers.
- Generate collectible characters with different traits and rarities.
- Produce NFT-ready images and metadata.
- Connect six separate chapters through a larger multichain mystery.
- Build a website for riddles, hidden archives, clues, and discoveries.
- Keep future games and utilities modular so they can be added later.

Core Features

1. Layered Artwork System

Characters will be assembled from transparent PNG layers.

Planned categories:

- "backgrounds" — colors, scenes, and environments.
- "bodies" — the master character body and silhouettes.
- "robes" — clothing, colors, and patterns.
- "eyes" — expressions and special eye designs.
- "faces" — masks, markings, and facial details.
- "symbols" — alchemy, geometry, and mysterious emblems.
- "accessories" — keys, crystals, pendants, and staffs.
- "effects" — halos, glow effects, and rare visual traits.
- "chapter_traits" — artwork associated with the six chapters.

Each layer must align with the master character template.

2. Collection Generator

The generator will eventually:

- Combine compatible artwork layers.
- Generate unique character images.
- Assign trait names and rarity weights.
- Prevent duplicate trait combinations where required.
- Export final PNG images.
- Generate JSON metadata for each character.
- Record trait combinations for reproducibility.

The initial goal is a small working prototype, not a complete collection generator.

3. Six-Chapter Multichain Mystery

Lil Omnis will have six distinct chapters. Each chapter will have its own identity, clues, artwork variations, and discoveries.

The chapters will be connected through a larger mystery that encourages collectors to investigate clues across different blockchain ecosystems.

The artwork and lore should support the multichain concept without requiring every collector to own NFTs on every chain.

Specific chain assignments and chapter lore will be defined separately.

4. Hidden Lore Archive

Future website features may include:

- Cryptic riddles.
- Hidden messages embedded in artwork.
- Unlockable archive entries.
- Cross-chapter clues.
- Collector discoveries.
- Secret symbols and historical records.
- A searchable lore archive.

The archive should support new discoveries without requiring a complete website rebuild.

Initial Technology

Keep the initial setup lightweight and free to develop.

- Artwork: ibis Paint X, Krita, or another editor that supports layers.
- Artwork format: Transparent PNG files.
- Metadata: JSON.
- Generator: JavaScript or TypeScript.
- Website: HTML, CSS, and JavaScript initially, with a framework added if needed.
- Version control: Git and GitHub.
- Hosting: GitHub Pages for a static website when appropriate.

No paid APIs or external generation services are required for the initial prototype.

Planned Repository Structure

lil-omnis/
├── README.md
├── docs/
│   ├── LORE.md
│   ├── ARTWORK_GUIDE.md
│   ├── TRAIT_SYSTEM.md
│   └── CHAPTERS.md
├── artwork/
│   ├── source/
│   ├── layers/
│   │   ├── backgrounds/
│   │   ├── bodies/
│   │   ├── robes/
│   │   ├── eyes/
│   │   ├── faces/
│   │   ├── symbols/
│   │   ├── accessories/
│   │   ├── effects/
│   │   └── chapter_traits/
│   └── previews/
├── generator/
│   ├── src/
│   ├── config/
│   └── output/
├── metadata/
│   ├── schema.json
│   └── examples/
├── website/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── .gitignore

Directories will be added as they become necessary. Do not create empty systems just to fill out the structure.

Development Roadmap

Phase 1 — Character Design

- [ ] Finalize the master Lil Omni design.
- [ ] Establish the character's proportions and outline.
- [ ] Create the first base character image.
- [ ] Establish layer naming and alignment rules.
- [ ] Export the first transparent PNG assets.

Phase 2 — Artwork Generator

- [ ] Load layers from organized folders.
- [ ] Combine layers in a consistent order.
- [ ] Generate a single character.
- [ ] Create trait-based metadata.
- [ ] Export a batch of test characters.
- [ ] Validate image and metadata consistency.

Phase 3 — Collection Design

- [ ] Define the six chapters.
- [ ] Create chapter-specific traits.
- [ ] Define rarity rules.
- [ ] Set collection size and supply rules.
- [ ] Validate uniqueness across generated characters.

Phase 4 — Lore Website

- [ ] Create a landing page.
- [ ] Introduce the six chapters.
- [ ] Build a basic lore archive.
- [ ] Add riddles and hidden discoveries.
- [ ] Prepare the architecture for future integrations.

Phase 5 — NFT Preparation

- [ ] Finalize collection artwork.
- [ ] Validate metadata and image files.
- [ ] Define chain-specific requirements.
- [ ] Test the intended marketplace upload process.
- [ ] Review the final collection before publication.

Development Principles

1. Keep the project modular and beginner-friendly.
2. Prefer free and open-source tools.
3. Avoid unnecessary dependencies and complicated infrastructure.
4. Keep artwork separate from code.
5. Never commit private keys, seed phrases, passwords, or API secrets.
6. Keep the original artwork editable and preserve source files.
7. Do not publish unreleased artwork or lore while the repository is private.
8. Make each feature independently testable.
9. Do not assume that NFT metadata or minting works identically across blockchains.

Current Status

Stage: Initial setup.

The first milestone is to create the master Lil Omni character and establish a working layered-artwork pipeline. The collection generator and website should be built around that design rather than creating separate, inconsistent character systems.

Project name: Lil Omnis

Core concept: Six chapters. Multiple chains. One connected mystery.
