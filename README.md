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

## Concept

An Edium is the main piece of information stored in DenseEdia, hence the name.
It has a title (required) and a kind (optional).

DenseEdia stores data like in a graph, which means you can draw links between
Edia. Each link can be directed or not, and have a label (optional).

To store more information in a Edium, you can set elements. They are values with
a precise type (NONE, BOOL, INT, FLOAT, STR, DATETIME) that are stored under a
certain name in an Edium. This value is versioned, so you can retrieve an
history of an element value over time.

## Usage

### Command line

#### Display the help

```bash
cd DenseEdia-Progressive/  # Move into the folder
source venv/bin/activate  # Enter the virtual environment

python -m denseedia --help  # Read the CLI documentation
python -m denseedia add-edium --help  # Read the documentation of the "add-edium" command
python -m denseedia edium --help  # Read the documentation of the "edium" group
```

You can find in the help some commands that are not presented in this README.

#### Add Edia

```bash
python -m denseedia add-edium "DenseEdia installation" -k event  # Add an event
python -m denseedia add-edium "Portal 2" -k event  # Add a game
python -m denseedia add-edium --url https://www.youtube.com/watch?v=q0pqJRUTQpY -k music  # Add a music you like
python -m denseedia add-edium "Perdu.com" --url https://www.perdu.com -k website -c "I love this website."  # Add a website with a comment
```

#### Display Edia

```bash
python -m denseedia list  # Show a list of all Edia
python -m denseedia edium 2 show  # Show the details (elements and links) of the Edium n°2
```

#### Draw links

```bash
python -m denseedia add-link 3 2 --label origin  # Draw a link from the 3rd Edium to the 2nd with label "origin"
```

#### Set elements

The element names are at your liking.

```bash
python -m denseedia edium 1 set comment "This will help me in the future."  # Set the element "comment"
python -m denseedia edium 1 set rating --type int 10 # Set the element "rating" to an integer value
python -m denseedia edium 1 set rating --type float --allow-type-change 9.5  # Set the element "rating" to a float value 
```

In this last case, as a safety measure, DenseEdia won't allow you to change the
value from an integer (10) to a float value (9.5), unless the
`-y/--allow-type-change` flag is given.

### HTTP API

#### Run

Run the API server with :

```bash
python -m denseedia start-server
```

Then, an interactive docs page is available at http://localhost:59130.

#### List of the endpoints

##### Edia

| Status | Method | URL        | Summary                  |
|:------:|:------:|------------|--------------------------|
|   X    |  GET   | `/edium`   | Get the list of all edia |
|   X    |  GET   | `/edium/5` | Get one edium            |
|   X    |  POST  | `/edium`   | Create one edium         |
|   X    | PATCH  | `/edium/5` | Modify one edium         |
|   X    | DELETE | `/edium/5` | Delete one edium         |

##### Elements and version :

| Status | Method | URL                                | Function                                             |
|:------:|:------:|------------------------------------|------------------------------------------------------|
|   X    |  GET   | `/edium/5/element?versions=none`   | Get the elements of one edium                        |
|   X    |  GET   | `/edium/5/element?versions=single` | Get the elements of one edium and their last version |
|   X    |  GET   | `/edium/5/element?versions=all`    | Get the elements of one edium and all their versions |
|   X    |  GET   | `/element/5?versions=none`         | Get one element                                      |
|   X    |  GET   | `/element/5?versions=single`       | Get one element and its last version                 |
|   X    |  GET   | `/element/5?versions=all`          | Get one element and all its versions                 |
|   X    |  POST  | `/edium/5/element`                 | Create one element and its last version              |
|   X    | PATCH  | `/element/5`                       | Modify one element                                   |
|   X    | DELETE | `/element/5`                       | Delete one element                                   |
|   X    |  POST  | `/element/5/version`               | Create a new version for an element                  |
|   X    | PATCH  | `/element/5/version`               | Modify the last version of an element                |
|   X    | DELETE | `/version/5`                       | Delete one version                                   |

##### Links :

| Status | Method | URL              | Function                               |
|:------:|:------:|------------------|----------------------------------------|
|   X    |  GET   | `/link`          | Get the list of all links              |
|   X    |  GET   | `/link/5`        | Get one link                           |
|   X    |  GET   | `/edium/5/links` | Get all links that have an edium in it |
|   X    |  POST  | `/link`          | Create one link                        |
|   X    | PATCH  | `/link/5`        | Modify one link                        |
|   X    | DELETE | `/link/5`        | Delete one link                        |

## The next step

Let's create issues for new ideas. It's more convenient.
