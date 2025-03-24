import flet as ft
import json
import math

unsupported_types: list[str] = [
    'chat_type',
    'event_type'
]

def delete_unsupported_keys(input_data: dict[str, str]):
    global unsupported_types
    for entry in unsupported_types:
        input_data.pop(entry, None)
    return input_data

def convert(text, group = 'main', format_end_string = False):
    '''
    Конвертация конфига старого формата в новый
    '''
    jsondict = None     # Общий словарь с конфигом: 'project_slug': {}
    try:
        # Удаляем запятую с конца, чтобы она не ломала JSON формат
        if text[-1] == ',':
            text = text[:-1]
            
        # Оборачиваем инпут кавычками для корректного JSON формата
        jsondict = json.loads('{' + text + '}')
    except Exception:
        return ''
    
    inputdict = jsondict[next(iter(jsondict))]      # Словарь с настройками конкретного проекта
    
    output = {next(iter(jsondict)): dict()}         # Общий выходной словарь: 'project_slug': {}
    params = output[next(iter(output))]             # Выходной словарь с настройками конкретного проекта
    
    if 'conditions' in inputdict:
        params['condition'] = convert_condition(inputdict['conditions'])
    
    if 'delay_range' in inputdict:
        delay_mid = math.floor(sum(inputdict['delay_range']) / len(inputdict['delay_range']))
        params['delay_s'] = delay_mid
        params['event_types'] = ['new_message', 'chat_open', 'ticket_reactivated_after_defer']
    
    if 'project_id' in inputdict:
        params['group'] = group
        params['project_slug'] = inputdict['project_id']
        params['slipped_out_messages_handling'] = 'wait_for_new_events'
        
    result = json.dumps(output, indent=4)
    result = result[6:-2]
    if format_end_string:
        result += ','
    return result

def convert_condition(input_data: dict[str, str], lastKey=''):
    '''
    Рекурсивная конвертация условия старого конфига в Pypred формат
    '''
    output_pypred = None
    input_data = delete_unsupported_keys(input_data)
    
    # Обрабатываем случаи, когда неявный оператор #and в старом конфиге
    if lastKey == '':
        if ('#or' in input_data.keys() or '#and' in input_data.keys()) and len(input_data) > 1:
            input_data = {'#and': [input_data]}
        elif '#or' not in input_data.keys() and '#and' not in input_data.keys() and len(input_data) > 1:
           input_data = {'#and': [input_data]}
    
    for key, value in input_data.items():
        if key == '#or' or key == '#and':
            if lastKey != '':
                output_pypred = list()
                output_pypred.append(dict())
                output_pypred[0]['operand'] = key[1:]
                if len(value) > 1:
                    output_pypred[0]['parts'] = [convert_condition({'#and': [x]}, key) for x in value]
                else:
                    output_pypred[0]['parts'] = [convert_condition(x, key) for x in value]
                 
                print(len(output_pypred[0]['parts']))    
                if len(output_pypred[0]['parts']) == 1:
                    output_pypred = output_pypred[0]['parts'][0]
            else:
                output_pypred = dict()
                output_pypred['operand'] = key[1:]
                output_pypred['parts'] = convert_condition(value[0], key)
                if len(output_pypred['parts']) == 1:
                    output_pypred = output_pypred['parts'][0]
        elif key == '#in':
            output_pypred = f'{lastKey} matches \'{'|'.join(value)}\''
        elif key == '#nin':
            output_pypred = f'{lastKey} not matches \'{'|'.join(value)}\''
        else:
            if key.startswith('meta_info'):
                key = key.replace('/', '.')
            if output_pypred is None:
                output_pypred = list()
            if type(value) is dict:
                if type(output_pypred) is list:
                    output_pypred.append(convert_condition(value, key))
                else:
                    output_pypred[key] = convert_condition(value, key)
            else:
                output_pypred.append(f'{key} matches {value}')
    
    return output_pypred
            
    

def main(page: ft.Page):
    page.title = "GIGA CONVERT"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bcolor = ft.colors.BLACK

    left_field_title = ft.Text(
        "Input",
        size=16,
        weight=ft.FontWeight.NORMAL,
        color=ft.colors.WHITE,
    )

    left_text_field = ft.TextField(
        multiline=True,
        min_lines=10,
        max_lines=10,
        width=400,
        border_color=ft.colors.WHITE,
        border_width=2,
        on_change=lambda e: update_right_field(e)
    )
    
    right_field_title = ft.Text(
        "Output",
        size=16,
        weight=ft.FontWeight.NORMAL,
        color=ft.colors.WHITE,
    )

    right_text_field = ft.TextField(
        multiline=True,
        min_lines=10,
        max_lines=10,
        width=400,
        read_only=True,
        border_color=ft.colors.WHITE,
        border_width=2,
    )
        
    background_image = ft.Image(
        src="orig.jpg",
        fit=ft.ImageFit.COVER,
        width=page.width,
        height=page.height
    )
    
    # Ссылка на GitHub-репозиторий
    github_link = ft.Text(
        "",
        size=16,
        color=ft.colors.WHITE,
        weight=ft.FontWeight.BOLD,
        spans=[
            ft.TextSpan(
                'https://github.com/AURUMVORXX/GIGA_CONVERT',
                url='https://github.com/AURUMVORXX/GIGA_CONVERT', 
                style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
            )
        ],
    )
    
    group_select_title = ft.Text('Группа:')
    group_select_buttons = ft.RadioGroup(content=ft.Column([
    ft.Radio(value="main", label="main"),
    ft.Radio(value="pre", label="pre")]), value='main', on_change=lambda e: update_right_field(e))
    
    format_end_string = ft.Checkbox(label='Добавить запятую в конце', on_change=lambda e: update_right_field(e))
    
    def update_right_field(e):
        right_text_field.value = convert(left_text_field.value, group_select_buttons.value, format_end_string.value)
        page.update()
    
    content=ft.Column([
        ft.Row(
            [
                ft.Column(
                    [
                        left_field_title,
                        left_text_field,
                    ],
                    spacing=10,
                ),
                ft.Column(
                    [
                        right_field_title,
                        right_text_field,
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=40,
        ),
        ],
        offset=ft.Offset(0, 0.8),
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        )
    
    main_container = ft.Column(
        [
            content,
            group_select_title,
            group_select_buttons,
            ft.Container(
                content=format_end_string,
                offset=ft.Offset(0, 2)
            ),
            ft.Container(
                content=github_link,
                alignment=ft.alignment.center,
                offset=ft.Offset(0, 12),
            ),
        ],
        expand=True,  # Растягиваем контейнер на всю высоту
    )
    
    stack = ft.Stack(
        [
            background_image,
            ft.Container(
                content=main_container,
                padding=20, 
            ),
        ],
        width=page.width,
        height=page.height,
    )
    
    page.add(stack)

ft.app(target=main, view=ft.WEB_BROWSER)