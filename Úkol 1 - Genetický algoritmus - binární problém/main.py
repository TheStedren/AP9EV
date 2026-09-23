import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Účelové funkce
def one_max(ind):
    return np.sum(ind)

def leading_ones(ind):
    cnt = 0
    for bit in ind:
        if bit == 1:
            cnt += 1
        else:
            break
    return cnt

# Selekční metody
def roulette_selection(pop, fitnesses):
    total_fit = np.sum(fitnesses)
    if total_fit <= 0:
        probs = np.ones(len(pop)) / len(pop)
    else:
        probs = fitnesses / total_fit
    idx = np.random.choice(len(pop), p=probs)
    return pop[idx]

def rank_selection(pop, fitnesses):
    ranks = np.argsort(np.argsort(fitnesses)) + 1
    probs = ranks / np.sum(ranks)
    idx = np.random.choice(len(pop), p=probs)
    return pop[idx]

# Genetické operátory
def crossover(p1, p2):
    if len(p1) < 2:
        return p1.copy(), p2.copy()
    pt = np.random.randint(1, len(p1))
    c1 = np.concatenate([p1[:pt], p2[pt:]])
    c2 = np.concatenate([p2[:pt], p1[pt:]])
    return c1, c2

def mutate(ind, mut_prob):
    mask = np.random.rand(len(ind)) < mut_prob
    ind[mask] = 1 - ind[mask]
    return ind

# Genetický algoritmus
def genetic_algorithm(D, obj_func, pop_size=50, elitism_ratio=0.15, mut_prob=0.01, max_evals=1000, selection='rank'):
    pop = np.random.randint(2, size=(pop_size, D))
    fitnesses = np.array([obj_func(ind) for ind in pop])
    evals = pop_size
    
    num_elite = max(1, int(pop_size * elitism_ratio))
    
    history_evals = [evals]
    history_best = [np.max(fitnesses)]
    best_overall = np.max(fitnesses)

    while evals < max_evals:
        sort_idx = np.argsort(fitnesses)[::-1]
        pop = pop[sort_idx]
        fitnesses = fitnesses[sort_idx]
        
        new_pop = []
        for i in range(num_elite):
            new_pop.append(pop[i].copy())
            
        while len(new_pop) < pop_size:
            if selection == 'roulette':
                p1 = roulette_selection(pop, fitnesses)
                p2 = roulette_selection(pop, fitnesses)
            else:
                p1 = rank_selection(pop, fitnesses)
                p2 = rank_selection(pop, fitnesses)
                
            c1, c2 = crossover(p1, p2)
            c1 = mutate(c1, mut_prob)
            c2 = mutate(c2, mut_prob)
            
            new_pop.append(c1)
            if len(new_pop) < pop_size:
                new_pop.append(c2)
                
        pop = np.array(new_pop)
        
        num_to_eval = min(pop_size - num_elite, max_evals - evals)
        for i in range(num_elite, num_elite + num_to_eval):
            fitnesses[i] = obj_func(pop[i])
            
        evals += num_to_eval
        
        current_best = np.max(fitnesses[:num_elite + num_to_eval])
        if current_best > best_overall:
            best_overall = current_best
            
        history_evals.append(evals)
        history_best.append(best_overall)
        
    return history_evals, history_best, best_overall

def main():
    runs = 10
    problems = {
        'One-Max': one_max,
        'Leading-Ones': leading_ones
    }

    dimensions = [10, 30, 100]

    stats = []

    for p_name, p_func in problems.items():
        plt.figure(figsize=(10, 6))
        for D in dimensions:
            max_evals = 100 * D
            
            pop_size = min(100, max(20, D))  
            mut_prob = 1.0 / D               
            
            all_interp_best = []
            eval_grid = np.linspace(0, max_evals, 200)
            final_bests = []
            
            for r in range(runs):
                h_evals, h_best, final_b = genetic_algorithm(
                    D, p_func, 
                    pop_size=pop_size, 
                    elitism_ratio=0.1, 
                    mut_prob=mut_prob, 
                    max_evals=max_evals, 
                    selection='rank'
                )
                final_bests.append(final_b)
                
                interp = np.interp(eval_grid, h_evals, h_best)
                all_interp_best.append(interp)
                
            mean_bests = np.mean(all_interp_best, axis=0)
            plt.plot(eval_grid, mean_bests, label=f'D={D}')
            
            stats.append({
                'Problém': p_name,
                'D (Délka)': D,
                'Nejlepší': np.max(final_bests),
                'Nejhorší': np.min(final_bests),
                'Průměr': np.mean(final_bests),
                'Medián': np.median(final_bests),
                'Směrodatná odchylka': np.round(np.std(final_bests), 2)
            })
            
        plt.title(f'Průměrný konvergenční graf ({runs} běhů) - {p_name}')
        plt.xlabel('Počet ohodnocení účelové funkce')
        plt.ylabel('Průměrná nejlepší hodnota fitness')
        plt.legend()
        plt.grid(True)

        filename = f"{p_name.lower()}_graf.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
    df_stats = pd.DataFrame(stats)
    
    csv_filename = "statistiky_ga.csv"
    df_stats.to_csv(csv_filename, index=False, encoding='utf-8-sig', sep=';')

    print(df_stats.to_markdown(index=False))

if __name__ == "__main__":
    main()