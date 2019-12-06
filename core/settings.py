from ruamel_yaml import YAML

MAX_GENERATION_NUMBER       = 20
POPULATION_SIZE             = 10
CROSSING_RATE               = 0.8
MUTATION_RATE               = 0.2
NUMBER_OF_ELITE_CHROMOSOMES = 1

RAW_DATA_FILE               = "core/raw_data.yml"
raw_data_file               = open(RAW_DATA_FILE)
RAW_DATA                    = YAML().load(raw_data_file.read())
raw_data_file.close()