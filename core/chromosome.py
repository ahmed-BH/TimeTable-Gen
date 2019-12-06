import random
import itertools
import numpy  as np 
import pandas as pd

class Chromosome():
    def __init__(self, **kargs):
        self.classes = ["c1", "c2"]     # kargs.get("classes", None)
        self.days    = ["d1", "d2", "d3", "d4", "d5"]     # kargs.get("days", None)
        self.hours   = ["h1","h2","h3", "h4", "h5"] # kargs.get("hours", None)
        # type verification
        # insert it here..
        # generate row_indexes for our dataframe, its purpose is for debuging and verifications
        index_rows = list(itertools.product(self.classes, self.days, self.hours))

        # column <course, room_type, lecturer, units>
        self.cols  = [("eng","A","l0",1),("fr","A","l1",1),("ia","A","l2",2),("ga","A","l3",1),("idx","A","l4",1),("tp_ga","TP","l5",2)] # kargs.get("course_room_lecturer_units", None)
        # type verification
        # insert it here..
        
        # chromosome is a list that determines the order we fill self.data
        self.chromosome = [i for i in range(len(self.cols))]
        random.shuffle(self.chromosome)
        
        # data is a matrix that contains all timetables 
        shape = (len(self.classes)*len(self.days)*len(self.hours), len(self.cols))
        self.genes = pd.DataFrame(np.zeros(shape),index=pd.MultiIndex.from_tuples(index_rows), columns=pd.MultiIndex.from_tuples(self.cols), dtype = np.int8)


    def get_chromosome(self):
        return self.chromosome
    
    def get_nb_genes(self):
        return len(self.cols)
        
    def fill_genes(self):
        # filling genes according to the rules...
        for working_column in self.chromosome:
            (course, type_room, lecturer, units) = self.cols[working_column]

            # rule 1: 
            #       * certain course respectively should be scheduled in class name i'th 
            #         then all rows cj ≠ i in that column should not be filled by 1
            #       * Others consecutive cells in the same day, as many as unit course 
            #         of that column, is also assigned 1
            for clss in self.classes:
                for unit in range(units):
                    (_, random_day, random_hour) = random.choice(self.genes.index)
                    if self.genes.loc[(clss, random_day, random_hour), (course, type_room, lecturer, units)] != -1:
                        self.genes.loc[(clss, random_day, random_hour), (course, type_room, lecturer, units)] = 1
                        
                        # rule 5: 
                        #       * If there is a cell in a column of a row (cx, di, hj) is equal to 1 
                        #         then for all row (cy, di, hj) have to be set -1 for cx ≠ cy at that column.
                        for clss2 in self.classes:
                            if clss != clss2:
                                self.genes.loc[(clss2, random_day, random_hour), (course, type_room, lecturer, units)] = -1


            # rule 3: For each row, there is only maximum a cell that is equal to 1.The others must be -1 or 0.
            (nb_rows, nb_cols) = self.genes.shape
            found_one          = False
            for i in range(nb_rows):
                found_one     = False
                not_to_change = -1
                for j in self.chromosome:
                    if self.genes.iloc[i,j] == 1 and found_one == False:
                        found_one     = True
                        not_to_change = j
                        continue
                    elif found_one == True:
                        break
                # correction phase..
                if found_one == True:
                    for k in self.chromosome:
                        if k != not_to_change:
                            self.genes.iloc[i,k] = -1

    def get_fitness(self):
        # the closet to 1, the better
        scheduled = 0
        (nb_rows, nb_cols) = self.genes.shape
        for i in range(nb_rows):
            for j in range(nb_cols):
                if self.genes.iloc[i,j] == 1:
                    scheduled+= 1
        
        all_units = 0
        for (_,_,_,u) in self.cols:
            all_units += u

        return scheduled/(len(self.classes)*all_units)

    def get_time_table(self, class_name):
        cols = self.days
        rows = self.hours
        time_table = pd.DataFrame(index=rows, columns=cols)

        for (row_class, row_day, row_hour) in self.genes.index:
            for (col_course, col_room, col_lecturer,_) in self.genes.columns:
                if row_class == class_name and self.genes.loc[(row_class, row_day, row_hour), (col_course, col_room, col_lecturer,_)] == 1:
                    time_table.loc[row_hour, row_day] = (col_course, col_lecturer, col_room)
        
        return time_table

        




     

 