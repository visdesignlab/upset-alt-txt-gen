class RegionClassification:
    def __init__(self):
        self.largest_data_region = None
        self.large_data_region = []
        self.medium_data_region = []
        self.small_data_region = []

    def set_largest(self, subset):
        self.largest_data_region = subset

    def add_to_large_region(self, subset):
        self.large_data_region.append(subset)

    def add_to_medium_region(self, subset):
        self.medium_data_region.append(subset)

    def add_to_small_region(self, subset):
        self.small_data_region.append(subset)

