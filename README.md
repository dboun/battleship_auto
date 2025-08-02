# Battleship AIs

- Make sure tkinter is setup
- Install numpy, pandas, tqdm, scikit-learn

## Gui

```bash
python3 gui.py
```

## Try your own model

- Inherit from ModelBase in model_base.py
- E.g. model_example.py
- To test your own model, change `ModelHardcoded` in `gui.py` change the following to your own.
        ```python
        self.game = Game(
            # player_1=ModelUser(fetch_user_move_callback=self.fetch_user_move_callback), 
            player_1=ModelHardcoded(),
            player_2=ModelHardcoded()
        )
        ```
- To interactively play against a model use `player_1=ModelUser(fetch_user_move_callback=self.fetch_user_move_callback)`.