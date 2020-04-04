import random
import math
import itertools
from scipy.stats import entropy as scipy_entropy
import numpy         as np 
import pandas        as pd


class Chromosome():
    def __init__(self, **kargs):
        data          = kargs.get("raw_data", None)
        assert data  != None, "'raw_data' must be specified"

        self.classes  = data["classes"]
        self.days     = data["days"] 
        self.hours    = data["hours"] 
        self.cols     = data["course_mapping"] 
        self.rooms    = data["rooms"]
        
        # -- constants to reduce len() times --
        self.LEN_ROOMS   = sum(self.rooms["number"])
        self.LEN_CLASSES = len(self.classes)
        self.LEN_DAYS    = len(self.days)
        self.LEN_HOURS   = len(self.hours)
        self.LEN_COLS    = len(self.cols)
        self.LEN_ROWS    = self.LEN_CLASSES * self.LEN_DAYS * self.LEN_HOURS 
        # -------------------------------------
             
        # chromosome is a list that determines the order we fill self.genes(our dataframe)
        self.chromosome = [i for i in range(self.LEN_COLS)]
        random.shuffle(self.chromosome)

        # keep track of available rooms.
        # 0: available, 1: not available at the given (day, time)
        self.available_room = np.zeros((self.LEN_DAYS * self.LEN_HOURS, self.LEN_ROOMS), dtype = np.int8)
        
        # genes is a dataframe that contains a timetable for all classes
        shape      = (self.LEN_CLASSES * self.LEN_DAYS * self.LEN_HOURS, self.LEN_COLS)
        self.genes = np.zeros(shape, dtype = np.int32)

    def get_chromosome(self):
        return self.chromosome
    
    def get_nb_genes(self):
        return self.LEN_COLS
    
    def init_genes(self):
        self.genes[:,:] = 0

    def fill_genes(self):
        # filling genes according to the rules...
        for working_column in self.chromosome:
            (_, room_type, _, units) = self.cols[working_column]

            # rule 1: 
            #       * certain course respectively should be scheduled in class name i'th 
            #         then all rows cj ≠ i in that column should not be filled by 1
            #       * Others consecutive cells in the same day, as many as unit course 
            #         of that column, is also assigned 1
            for clss in range(self.LEN_CLASSES):
                start     = clss * self.LEN_DAYS * self.LEN_HOURS
                end       = (clss+1) * self.LEN_DAYS * self.LEN_HOURS - 1
                RAND_ROW  = random.randint(start, end)
                RAND_DAY  = (RAND_ROW % (self.LEN_DAYS * self.LEN_HOURS)) // self.LEN_HOURS
                
                reserved_units = 0
                for hour in range(self.LEN_HOURS):
                    if reserved_units == units:
                        break
                    tmp_row = start + RAND_DAY * self.LEN_HOURS + hour
                    # choosing a random column in available_rooms np table
                    tmp_i = self.rooms["type"].index(room_type)
                    if tmp_i == -1: raise ValueError("rooms type does not exist")
                    s   = sum(self.rooms["number"][0:tmp_i])
                    e   = s + self.rooms["number"][tmp_i] - 1
                    rand_room = random.randint(s, e)
                    # -----------------------------------------------------
                    if self.genes[tmp_row, working_column] == 0 and self.available_room[hour*RAND_DAY, rand_room] == 0:
                        self.available_room[hour*RAND_DAY, rand_room] = 1
                        self.genes[tmp_row, working_column] = rand_room + 1 # saving the room
                        reserved_units += 1
                        
                        # rule 5: 
                        #       * If there is a cell in a column of a row (cx, di, hj) is equal to 1 
                        #         then for all row (cy, di, hj) have to be set -1 for cx ≠ cy at that column.
                        BASE  = tmp_row % (self.LEN_DAYS * self.LEN_HOURS)
                        for clss2 in range(self.LEN_CLASSES):
                            if clss != clss2:
                                self.genes[BASE, working_column] = -1
                            BASE += self.LEN_DAYS * self.LEN_HOURS

                        # rule 3: 
                        #    For each row, there is only maximum a cell that is equal to 1.
                        #    The others must be -1 or 0.
                        for col in range(self.LEN_COLS):
                            if col != working_column:
                                self.genes[tmp_row, col] = -1

    def get_entropy(self, class_name):
        # if all units of a course is sheduled in the same day then return 1
        # else return 0
        u_per_day_mat = np.zeros((self.LEN_COLS, self.LEN_DAYS), dtype=np.uint8)

        # filling the vector
        class_name = self.classes.index(class_name)
        for day in range(self.LEN_DAYS):
            sum_of_1 = 0
            for hour in range(self.LEN_HOURS):
                for row in range(u_per_day_mat.shape[0]):
                    indx = hour + day*self.LEN_HOURS + class_name * self.LEN_DAYS * self.LEN_HOURS
                    if self.genes[indx, row] > 0:
                        u_per_day_mat[row, day] += 1
        
        # calculating the entropy
        all_entropies = 0
        for row in range(u_per_day_mat.shape[0]):
            entropy = scipy_entropy(u_per_day_mat[row,:], base=2)
            if entropy == True:
                all_entropies  += entropy
        
        return all_entropies/self.LEN_COLS

    def get_fitness(self):
        # the closet to 1, the better
        scheduled = 0
        (nb_rows, nb_cols) = self.genes.shape
        for i in range(nb_rows):
            for j in range(nb_cols):
                if self.genes[i,j] > 0:
                    scheduled+= 1
        
        all_units = 0
        for (_,_,_,u) in self.cols:
            all_units += u

        fitness = scheduled/(self.LEN_CLASSES*all_units)
        
        # use entrepy to update fitness
        # the importance of entropy is 20% of fitness
        for clss in self.classes:
            fitness -= (self.get_entropy(clss)/self.LEN_CLASSES)*0.2
        
        return fitness

    def get_time_table(self, class_name):
        time_table = pd.DataFrame(index=self.hours, columns=self.days)

        class_name = self.classes.index(class_name)
        for day in range(self.LEN_DAYS):
            for hour in range(self.LEN_HOURS):
                for col in range(self.LEN_COLS):
                    indx = hour + day * self.LEN_HOURS + class_name * self.LEN_DAYS * self.LEN_HOURS
                    if self.genes[indx, col] > 0:
                        (subject, room_type, lecturer, _) = self.cols[col]
                        # ---------- get right room number ----------
                        i    = self.rooms["type"].index(room_type)
                        diff = sum(self.rooms["number"][0:i])
                        room_number = self.genes[indx, col] - 1 - diff
                        # -------------------------------------------
                        time_table.iloc[hour, day] = "{}, {}:{}".format(subject, room_type, room_number)
        return time_table

        




     

 