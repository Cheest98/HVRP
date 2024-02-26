import pandas as pd
import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial.distance import cityblock, euclidean
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import random

root = Tk()
root.title('Genetic algoritm for HVRP')
root.maxsize(1200, 1200)
root.config(bg="grey")
#width=1200, height=200

UI_frame = Frame(root, width=1200, height=200, bg='grey')
UI_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

canvas = Canvas(root, width=500, height=500, bg='white')
canvas.grid(row=1, column=0, padx=0, pady=0)
canvasdwa = Canvas(root, width=500, height=500, bg='white')
canvasdwa.grid(row=1, column=1, padx=0, pady=0)


class node:
    def __init__(self, i, x, y, size):
        self.i = i
        self.x = x
        self.y = y
        self.size = size

    def __str__(self):
        return str(self.i)


class truck:
    def __init__(self, i, size, cost):
        self.i = i
        self.size = size
        self.cost = cost



def Generate():
    x = float(proEntry.get())
    z = int(iterEntry.get())
    j = int(popjEntry.get())
    d = int(popdEntry.get())

    data_3 = 'c20_3mix.txt'
    data_5 = 'c20_5mix.txt'

    columns = ['i', 'x', 'y', 'size']
    df_nodes = pd.read_csv(data_3, names=columns, delimiter="  ", engine='python', header=1,
                           skiprows=[i for i in range(22, 30)])
    print(df_nodes)

    columns = ['i', 'size', 'cost']
    df_trucks_3 = pd.read_csv(data_3, names=columns, delimiter='  | ', engine='python',
                              skiprows=[i for i in range(0, 25)])
    df_trucks_5 = pd.read_csv(data_5, names=columns, delimiter='  | ', engine='python',
                              skiprows=[i for i in range(0, 25)])

    print(df_trucks_3)

    nodes = []
    for i, row in df_nodes[1:].iterrows():
        nodes.append(node(row.i, row.x, row.y, row['size']))
    deposit = node(df_nodes.iloc[0].i, df_nodes.iloc[0].x, df_nodes.iloc[0].y, df_nodes.iloc[0]['size'])

    # parametry
    mutation_probability = x
    population_sizes = [j, d]
    number_of_iterations = [z]

    # Algorytm

    df_trucks_all = [df_trucks_3, df_trucks_5]
    results = {z: []}

    def assign_best_tracks(chromosome, population_size, trucks, deposit):
        G = nx.DiGraph()

        G.add_node(deposit.i)
        for node in chromosome:
            G.add_node(node.i)

        for j, truck in enumerate(trucks):
            for i, node in enumerate(chromosome):
                chromosomes_after_node = chromosome[i + 2:]
                farest_node = find_farest_node(node, truck.size,
                                               chromosomes_after_node)  # where i can get with my capacity

                distance_cost = truck.cost * distance(deposit, node)
                distance_cost = distance_cost + truck.cost * distance(node, farest_node)

                G.add_edge(node.i, farest_node.i, weight=distance_cost, truck=j)
        path = nx.shortest_path(G, source=chromosome[0].i, target=chromosome[len(chromosome) - 1].i, weight="weight")
        t = []
        for i in range(len(path) - 1):
            t.append(G[path[i]][path[i + 1]]['truck'])
        cost = 0
        for i in range(len(path) - 1):
            cost = cost + G[path[i]][path[i + 1]]['weight']
        return cost, t, path

    # nx.draw(G)
    #  plt.show()

    def distance(node_1, node_2):
        return euclidean([node_1.x, node_1.y], [node_2.x, node_2.y])

    def find_farest_node(current_node, truck_size, chromosome):
        current_size = 0
        farest_node = node(0, 0, 0, 0)

        for n in chromosome:
            if n.size + current_size < truck_size:
                current_size = current_size + n.size
                farest_node = n
            else:
                break
        return farest_node

    # parent selection
    def select_parents(fitness, population):
        maxes = sum(fitness)
        pick_1 = np.random.uniform(0, maxes)
        parent_1 = 0
        current = 0

        for i, fit in enumerate(fitness):
            current = current + fit
            if current > pick_1:
                parent_1 = i
                break

        parent_2 = parent_1

        while parent_2 == parent_1:
            current = 0
            pick_2 = np.random.uniform(0, maxes)
            for i, fit in enumerate(fitness):
                current = current + fit
                if current > pick_2:
                    parent_2 = i
                    break

        return population[parent_1], population[parent_2]

    # Krzyżowanie
    def crossover(parent1, parent2):
        children = []
        cross_start = np.random.randint(0, parent1.size)
        cross_end = np.random.randint(0, parent1.size)

        while cross_start >= cross_end:
            cross_start = np.random.randint(0, parent1.size)
            cross_end = np.random.randint(0, parent1.size)

        child1 = parent1[cross_start:cross_end]
        child2 = parent2[cross_start:cross_end]

        before_inherit_size = len(parent1[:cross_start])
        after_inherit_size = len(parent1[cross_end:])

        gen_parent1 = 0
        gen_parent2 = 0

        if before_inherit_size > 0:

            child1_before_inherit = [deposit] * before_inherit_size
            child2_before_inherit = [deposit] * before_inherit_size

            for i in range(before_inherit_size):
                found = [False, False]

                while not found[0]:
                    if parent1[gen_parent1] not in child2:
                        child2_before_inherit[i] = parent1[gen_parent1]
                        found[0] = True
                    gen_parent1 += 1

                while not found[1]:
                    if parent2[gen_parent2] not in child1:
                        child1_before_inherit[i] = parent2[gen_parent2]
                        found[1] = True
                    gen_parent2 += 1

            child1_before_inherit.extend(child1)
            child1 = child1_before_inherit

            child2_before_inherit.extend(child2)
            child2 = child2_before_inherit

        if after_inherit_size < len(parent1):

            child1_after_inherit = [deposit] * after_inherit_size
            child2_after_inherit = [deposit] * after_inherit_size

            for i in range(after_inherit_size):

                found = [False, False]

                while not found[0]:
                    if parent1[gen_parent1] not in child2:
                        child2_after_inherit[i] = parent1[gen_parent1]
                        found[0] = True
                    gen_parent1 += 1

                while not found[1]:
                    if parent2[gen_parent2] not in child1:
                        child1_after_inherit[i] = parent2[gen_parent2]
                        found[1] = True
                    gen_parent2 += 1

            child1 = list(child1)
            child1.extend(child1_after_inherit)

            child2 = list(child2)
            child2.extend(child2_after_inherit)

        children.append(list(child1))
        children.append(list(child2))

        return children

    def mutation(chrom):
        i, j = (0, 1)

        while i < len(chrom) - 1:

            restart_search = False

            while j < len(chrom):

                mutated = chrom.copy()
                mutated[i], mutated[j] = mutated[j], mutated[i]

                cost_1, _, _ = assign_best_tracks(mutated, population_size, trucks, deposit)
                cost_2, _, _ = assign_best_tracks(chrom, population_size, trucks, deposit)

                if cost_1 < cost_2:
                    chrom = mutated
                    restart_search = True
                    break
                else:
                    j += 1

            if not restart_search:
                i, j = (i + 1, 0)
            else:
                i, j = (0, 1)

        return chrom

    for n in number_of_iterations:
        for pop_index, population_size in enumerate(population_sizes):
            print(results)
            results[int(n)].append([])
            for truck_index, df_trucks in enumerate(df_trucks_all):

                results[int(n)][pop_index].append([])

                trucks = []
                for i, row in df_trucks.iterrows():
                    trucks.append(truck(row.i, row['size'], row.cost))

                fitness = []
                fitness.append(2.0 / population_size)
                for i in range(1, population_size):
                    fitness.append(
                        fitness[i - 1] + 2.0 * (population_size - i - 1) / (population_size * (population_size - 1)))

                population = []

                for _ in range(population_size):  # Utworzenie populacji
                    chromosome = np.random.permutation(nodes)  # Utworzenie chromosomu
                    cost, t, path = assign_best_tracks(chromosome, population_size, trucks,
                                                       deposit)  # Obliczenie kosztu
                    population.append({"population": chromosome, "cost": cost, "trucks": t, "trucks_switch": path})

                population = sorted(population, key=lambda i: i['cost'])

                for k in range(n):
                    ## generate children

                    fitness = []
                    fitness.append(2.0 / len(population))
                    for i in range(1, len(population)):
                        fitness.append(
                            fitness[i - 1] + 2.0 * (len(population) - i - 1) / (
                                        len(population) * (len(population) - 1)))

                    parent_1, parent_2 = select_parents(fitness, population)

                    assert len(parent_1['population']) == len(nodes), 'error in parent_1 after selection'
                    assert len(parent_2['population']) == len(nodes), 'error in parent_2 after selection'

                    child1, child2 = crossover(parent_1['population'], parent_2['population'])

                    assert len(child1) == len(nodes), 'error in child1 after crossover'
                    assert len(child2) == len(nodes), 'error in child2 after crossover'

                    ## add children to population
                    cost, t, path = assign_best_tracks(child1, population_size, trucks, deposit)  # Obliczenie kosztu
                    population.append(
                        {"population": np.array(child1), "cost": cost, "trucks": t, "trucks_switch": path})

                    cost, t, path = assign_best_tracks(child2, population_size, trucks, deposit)  # Obliczenie kosztu
                    population.append(
                        {"population": np.array(child2), "cost": cost, "trucks": t, "trucks_switch": path})

                    los = random.random()

                    if los < mutation_probability:
                        child2 = mutation(child2)

                        cost, t, path = assign_best_tracks(child2, population_size, trucks,
                                                           deposit)  # Obliczenie kosztu
                        child2_chromosme = {"population": np.array(child2), "cost": cost, "trucks": t,
                                            "trucks_switch": path}

                        assert len(child2) == len(nodes), 'error in mutation'

                        population = sorted(population, key=lambda d: d['cost'], reverse=True)

                        half_population_size = len(population) / 2
                        replace_index = np.random.randint(half_population_size, len(population))
                        population[replace_index] = child2_chromosme

                    population = sorted(population, key=lambda d: d['cost'])
                    results[int(n)][pop_index][truck_index].append(population[0]['cost'])

    results[z][0][0]  # pop 50, truck 3
    results[z][0][1]  # pop 50, truck 5
    results[z][1][0]  # pop 100, truck 3
    results[z][1][1]  # pop 100, truck 5

    import _pickle as pickle

    with open("results_real.txt", 'wb') as file:
        file.write(pickle.dumps(results))  # use `pickle.loads` to do the reverse


    #przerabianie zmiennych


    Best = str(int(results[z][0][0][-1])) # pop j, truck 3
    Best1 = str(int(results[z][0][1][-1])) #pop j, truck 5
    Best2 = str(int(results[z][1][0][-1])) # pop d, truck 3
    Best3 = str(int(results[z][1][1][-1])) #pop d, truck 5
    pltIter=str(z)
    pltPopJeden=str(j)
    pltPopDwa=str(d)

    fig = plt.figure()
    fig.suptitle("Ilość iteracji " + pltIter + ", 5 pojazdów")

    plt.xlabel('iteration')
    plt.ylabel('cost')

    plt.plot(results[z][0][1], label='population ' +  pltPopJeden)
    plt.plot(results[z][1][1], label='population ' +  pltPopDwa)

    fig.legend()
    plt.annotate("Populacja: " +  pltPopJeden +" najlepszy " +  Best1 +
             "\nPopulacja: " +pltPopDwa +" najlepszy " + Best3, (0, 0), (-20, -17), xycoords='axes fraction', textcoords='offset points', va='top', fontsize=8)
    plt.savefig('I5T5.png')
    plt.show()

    fig = plt.figure()
    fig.suptitle("Ilość iteracji " + pltIter +", 3 pojazdy")

    plt.xlabel('iteration')
    plt.ylabel('cost')

    plt.plot(results[z][0][0], label='Population ' +  pltPopJeden)
    plt.plot(results[z][1][0], label='population ' +  pltPopDwa)

    fig.legend()
    #fig.text(0.5, 0.02, "Najlepszy wynik dla populacji " + pltPopJeden + "to " + Best +
             #"\n Najlepszy wynik dla populacji: " + pltPopDwa + " to" + Best2, ha="center", fontsize=10, )
    plt.annotate("Populacja: " +  pltPopJeden +" najlepszy " +  Best +
             "\nPopulacja: " +pltPopDwa +" najlepszy " + Best2, (0, 0), (-20, -17), xycoords='axes fraction', textcoords='offset points', va='top', fontsize=8)
    plt.savefig('I5T3.png')
    plt.show()

    print("Prawdopodobieństwo mutacji: ", x)
    print("Ilośc iteracji", z)
    print("Populacja pierwsza: ", j)
    print("Populacja druga", d)
    print(Best)
    print(Best1)
    print(Best2)
    print(Best3)
    print()
    image = Image.open('I5T3.png')
    canvas.image = ImageTk.PhotoImage(image.resize((459, 459), Image.ANTIALIAS))
    canvas.create_image(0, 0, image=canvas.image, anchor='nw')
    imagedwa = Image.open('I5T5.png')
    canvasdwa.image= ImageTk.PhotoImage(imagedwa.resize((450, 450), Image.ANTIALIAS))
    canvasdwa.create_image(0, 0, image=canvasdwa.image, anchor='nw')

#Row[1]
Label(UI_frame, text="Prawdopodobieństwo: ", bg='grey').grid(row=0, column=0, padx=5, pady=5, sticky=W)
proEntry = Entry(UI_frame)
proEntry.grid(row=0, column=1, padx=5, pady=5, sticky=W)

Label(UI_frame, text="Ilość iteracji: ", bg='grey').grid(row=0, column=3, padx=5, pady=5, sticky=W)
iterEntry = Entry(UI_frame)
iterEntry.grid(row=0, column=4, padx=5, pady=5, sticky=W)

Label(UI_frame, text="Populacja 1:", bg='grey').grid(row=1, column=0, padx=5, pady=5, sticky=W)
popjEntry = Entry(UI_frame)
popjEntry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
Label(UI_frame, text="Populacja 2:", bg='grey').grid(row=1, column=3, padx=5, pady=5, sticky=W)
popdEntry = Entry(UI_frame)
popdEntry.grid(row=1, column=4, padx=5, pady=5, sticky=W)
Button(UI_frame, text="Start", command=Generate, bg='red').grid(row=3, column=2, padx=5, pady=5)


root.mainloop()