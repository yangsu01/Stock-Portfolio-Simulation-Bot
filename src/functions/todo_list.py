import json

from functions.constants import TODO_LIST_PATH

def get_list(user: str) -> list:
    """Gets the user's current todo list
    
    Args:
        user (str): the users name
        
    Returns:
        list: list of todo items
    """
    with open(TODO_LIST_PATH, 'r') as read_path:
            data = json.load(read_path)

    if user not in data:
        raise Exception(f"{user} does not have a todo list")
    elif len(data.get(user)) == 0:
        raise Exception(f"{user}'s todo list is empty")
    else:
        todo = f'Current TODO list for {user}\n'
        for i, item in enumerate(data.get(user)):
            todo += f'> {i+1}.{item}\n'
        
        return todo


def add_item(user: str, item: str) -> None:
    """Adds an item to the todo list
    
    Args:
        user (str): the users name
        item (str): item to add to list
    """
    with open(TODO_LIST_PATH, 'r') as read_path:
            data = json.load(read_path)

    if user in data:
        data[user].append(item)
    else:
        data[user] = [item]
    
    with open(TODO_LIST_PATH, 'w') as write_path:
        json.dump(data, write_path, indent=4)



def mark_complete(user: str, index: int) -> None:
    """Marks a todo list item as complete
    
    Args:
        user (str): the users name
        index (int): index of the item
    """
    with open(TODO_LIST_PATH, 'r') as read_path:
        data = json.load(read_path)
    
    if index not in range(len(data.get(user))):
        raise ValueError('Index does not exist')
    else:
        data.get(user).pop(index)
        with open(TODO_LIST_PATH, 'w') as write_path:
            json.dump(data, write_path, indent=4)
