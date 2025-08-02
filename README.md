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
- To test your own non-random-model, in engine change the following to your own.
        ```python
                self.player_1 = ModelBase()
                self.player_2 = ModelBase()
        ```