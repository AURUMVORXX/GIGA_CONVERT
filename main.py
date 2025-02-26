import flet as ft
import json
import math

def convert(text):
    try:
        if text[-1] == ',':
            text = text[:-1]
        jsondict = json.loads('{' + text + '}')
    except Exception:
        return ''
    
    inputdict = jsondict[next(iter(jsondict))]
    
    output = {next(iter(jsondict)): dict()}
    params = output[next(iter(output))]
    
    if 'conditions' in inputdict:
        params['condition'] = convert_condition(inputdict['conditions'])
    
    if 'delay_range' in inputdict:
        delay_mid = math.floor(sum(inputdict['delay_range']) / len(inputdict['delay_range']))
        params['steps'] = {'delay_s': delay_mid, 'event_types': ['new_message', 'chat_open']}
    
    if 'project_id' in inputdict:
        params['project_slug'] = inputdict['project_id']
        
    params['slipped_out_messages_handling'] = 'wait_for_new_events'
        
    return json.dumps(output, indent=4)
    
def convert_condition(input_data):
    output_pypred = ''
    
    if type(input_data) == dict:
        for key, value in input_data.items():
            
            if key == '#or':
                output_pypred += '('
                for cond in value:
                        
                    if len(output_pypred) != 1:
                        output_pypred += ' or '
                        
                    converted_cond = convert_condition(cond)
                    if len(converted_cond) != 0:
                        output_pypred += f'({converted_cond})'
                
                if output_pypred.endswith(' or '):
                    output_pypred = output_pypred[:-4]
                output_pypred += ')'
                    
            if key == '#and':
                output_pypred += '('
                for cond in value:
                        
                    if len(output_pypred) != 1:
                        output_pypred += ' and '
                        
                    converted_cond = convert_condition(cond)
                    if len(converted_cond) != 0:
                        output_pypred += f'({converted_cond})'
                
                if output_pypred.endswith(' and '):
                    output_pypred = output_pypred[:-5]
                output_pypred += ')'
                    
            if key == '#not':
                output_pypred += f'not {convert_condition(value)}'
                
            if key == "#exists":
                if value == True:
                    output_pypred += f'is not undefined'
                else:
                    output_pypred += f'is undefined'
                    
            if key == '#in':
                output_pypred += 'matches \''
                for cond in value:
                    
                    output_pypred += f'{cond}|'
                output_pypred = output_pypred[:-1] + '\''
                
            if key == '#nin':
                output_pypred += 'not matches \''
                for cond in value:
                    
                    output_pypred += f'{cond}|'
                output_pypred = output_pypred[:-1] + '\''
                    
            if key == 'line':
                
                if len(output_pypred) != 0:
                    output_pypred += ' and '
                    
                output_pypred = f'line {convert_condition(value)}'
                
            if key.startswith('meta_info'):
                
                if len(output_pypred) != 0:
                    output_pypred += ' and '
                    
                meta_name = key.replace('/', '.')
                output_pypred += f'{meta_name} {convert_condition(value)}'
                
    elif type(input_data) == str:
        return f"== '{input_data}'"
    else:
        return f"== {input_data}"
                
                    
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
    def update_right_field(e):
        right_text_field.value = convert(left_text_field.value)
        page.update()
        
    # Добавляем элементы на страницу
    page.add(
    ft.Column([
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
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        )
    )

ft.app(target=main)