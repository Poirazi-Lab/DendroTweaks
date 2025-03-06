import pandas as pd

class SWCReader():
    """
    Reads an SWC file and returns a DataFrame.
    """

    def __init__(self):
        pass

    @staticmethod
    def read_file(path_to_swc_file: str) -> pd.DataFrame:
        """
        Read the SWC file and return a DataFrame.
        """
        with open(path_to_swc_file, 'r') as f:
            lines = f.readlines()
        lines = [' '.join(line.split()) for line in lines if line.strip()]
        with open(path_to_swc_file, 'w') as f:
            f.write('\n'.join(lines))

        df = pd.read_csv(
            path_to_swc_file, 
            sep=' ', 
            header=None, 
            comment='#', 
            names=['Index', 'Type', 'X', 'Y', 'Z', 'R', 'Parent'],
            index_col=False
        )

        if (df['R'] == 0).all():
            df['R'] = 1.0

        if df['Index'].duplicated().any():
            raise ValueError("The SWC file contains duplicate node ids.")
        return df

    @staticmethod
    def plot_raw_data(df, ax):
        """
        Plot the raw data from the SWC file using the DataFrame.
        """
        types_to_colors = {1: 'C1', 2: 'C3', 3: 'C2', 4: 'C0', 31: 'green', 41: 'blue', 42: 'magenta', 43: 'brown'}
        for t in df['Type'].unique():
            color = types_to_colors.get(t, 'k')
            mask = df['Type'] == t
            ax.scatter(df[mask]['X'], df[mask]['Y'], df[mask]['Z'], 
                       c=color, s=1, label=f'Type {t}')
        ax.legend()