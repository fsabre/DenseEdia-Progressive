# DenseEdia - Progressive

One more DenseEdia, one step at a time.

I'm tired of coding this project again and again just to drop it after a while.
So this time, it will be done bit by bit, following what I need. I WON'T FEAR
NEITHER THE REFACTORING NOR THE BREAKING CHANGES. And maybe I'll be in peace
once again.

## What is DenseEdia ?

Explaining one more time, are we ? It's meant to store things. Of any kinds.
With any fields. And links between. Why not using database engine ? At this
point, I don't remember, but I have a dream, as they say.

## Installation

On Unix :

```bash
git clone https://github.com/fsabre/DenseEdia-Progressive  # Clone the project
cd DenseEdia-Progressive/  # Move into the folder
python3 -m venv venv  # Create a virtual environment
source venv/bin/activate  # Enter it
pip install -r requirements.txt  # Install the dependencies ... and it's done.
```

It's totally possible to use it on Windows/MacOS/etc, but the explanations will
wait for now.

## Usage

```bash
cd DenseEdia-Progressive/  # Move into the folder
source venv/bin/activate  # Enter the virtual environment

python -m denseedia --help  # Read the CLI documentation
python -m denseedia add --help  # Read the documentation of the "add" command
python -m denseedia add "DenseEdia installation" -k event  # Add an event
python -m denseedia add --url https://www.youtube.com/watch?v=q0pqJRUTQpY -k music  # Add a music you like
python -m denseedia add "Perdu.com" --url https://www.perdu.com -k website -c "I love this website."  # Add a website with a comment
```

## The next step

Let's create issues for new ideas. It's more convenient.
