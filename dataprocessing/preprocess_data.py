import csv

def delete_first_n_rows(input_file, output_file, delete_lines):
    with open(input_file, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        data = list(csvreader)
    
    if len(data) <= delete_lines:
        print("The CSV file contains fewer than five rows. Nothing to delete.")
        return
    
    data = data[delete_lines:]  # Skip the first five rows
    
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)

def write_matrix_to_csv_with_index(matrix, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for idx, row in enumerate(matrix, start=1):
            csvwriter.writerow([idx] + row)

def make_length_same(input_file_1, input_file_2, output_file_1, output_file_2):
    with open(input_file_1, newline='') as file:
        reader = csv.reader(file, delimiter = ',')
        data_1 = list(reader)
    with open(input_file_2, newline='') as file:
        reader = csv.reader(file, delimiter = ',')
        data_2 = list(reader)
        
    if len(data_1) > len(data_2):
        data_1 = data_1[:len(data_2)]
    elif len(data_1) < len(data_2):
        data_2 = data_2[:len(data_1)]
        
    with open(output_file_1, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data_1)
    with open(output_file_2, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data_2)

def get_csv_row_without_first_column(file_path, row_index):
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        rows = list(csvreader)
    
    if row_index < 0 or row_index >= len(rows):
        raise IndexError("Row index is out of range.")
    
    row_data = rows[row_index][1:]  # Excluding the first column
    
    return row_data

def get_first_column(csv_file, xsens_file):
    first_column = []
    with open(csv_file, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter = ',')
        # print(csvreader)
        # first_data = list(csvreader)[0][0]
        # print("type of first data: ", type(first_data))
        for row in list(csvreader):
            if row:  # Check if the row is not empty
                first_column.append(int(row[0]))
    first_index = first_column[0]
    for i in range(len(first_column)):
        first_column[i] = first_column[i] - first_index
        
    # if xsens_file == True:
    #     first_column = first_column[:len(first_column)//2]
    return first_column

def count_csv_rows(file_path):
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        row_count = sum(1 for _ in csvreader)
    return row_count

def list_half(list):
    result = []
    for i in range(len(list)//2):
        result.append((list[i*2]+list[i*2+1])/2)
    return result