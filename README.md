# Battleship AIs

Well, this was supposed to be NNs trained for playing battleship, but turns out the game is kinda easy so heuristics gets you 95% to optimal play. So now it's that.

## Install

- Make sure tkinter is setup (in ubuntu-based that is `sudo apt install python3-tk`)
- `pip install -r requirements.txt`

## Use

#### Let the algorithm battle itself

```bash
python3 gui.py
```

#### Battle against it (interactive, click on squares)

I `gui.py`, change:

```
player_1=ModelHardcoded(),
```

to

```
player_1=ModelUser(fetch_user_move_callback=self.fetch_user_move_callback), 
```

## Try your own model

- Inherit from ModelBase in model_base.py
- E.g. model_example.py
- To test your own model, in `gui.py` change the following to your own to your own class.
        ```python
        self.game = Game(
            player_1=ModelHardcoded(),
            player_2=ModelHardcoded()
        )
        ```