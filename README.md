
### Setul de teste folosite pentru validare

Setul de date de intrare folosite pentru a valida si evalua algoritmii propusi pentru problema Bin Packing este alcatuit din:
- 100 teste cu n <= 30, folosite pentru a compara solutia data de algoritmii euristici cu solutia optima data de brute force.
- 40 teste cu n <= 1000, folosite pentru a testa algoritmii euristici intre ei, comparand atat timpul de executie si scalabilitatea, cat si rezultatele acestora.

Toate testele folosesc distributii variate pentru a genera valori random.
Pentru fiecare categorie de teste, se folosesc urmatoarele distributii:
- Distributie uniforma - random.randint(1, C)
- Multe valori mici - vi >= 1, vi <= C // 4
- Multe valori mari - vi >= C // 2, vi <= C
- In jurul capacitatii pe 2 - vi >= C // 3, vi <= 2C // 3


# Setup

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt