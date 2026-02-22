#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI模拟法庭服务
提供HTTP接口供后端调用
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import requests
import json
import threading
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from court_debate_sdk import CourtDebateModel

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局模型实例
_model = None
_model_lock = False

# 模型初始化状态
_model_init_status = {
    'initializing': False,
    'loaded': False,
    'error': None,
    'progress': '',
    'progress_steps': []
}
_model_init_lock = threading.Lock()

# 外部AI API配置
EXTERNAL_AI_API_KEY = "sk-aslsGiKSQWdlPmXad3StwEY1BEJFpjh4wAwLEWlxUltcNqfi"
EXTERNAL_AI_BASE_URL = "https://chatapi.zjt66.top/v1"
EXTERNAL_AI_MODEL = "gpt-4o-mini"


def resolve_model_path(adapter_dir: str) -> str:
    """解析模型路径，支持相对路径和绝对路径"""
    # 如果是绝对路径，直接返回
    if os.path.isabs(adapter_dir):
        if not os.path.exists(adapter_dir):
            raise FileNotFoundError(f"模型目录不存在: {adapter_dir}")
        return adapter_dir
    
    # 相对路径：尝试多个可能的位置（去重）
    # 优先检查项目根目录，因为模型目录应该在项目根目录下
    script_dir = os.path.dirname(os.path.abspath(__file__))  # ai_service 目录
    project_root = os.path.dirname(script_dir)  # 项目根目录 D:\MootAI
    current_work_dir = os.getcwd()
    
    # 收集所有可能的路径（去重，按优先级排序）
    candidate_paths = []
    path_labels = []
    
    # 1. 项目根目录（最高优先级，模型目录应该在项目根目录下）
    project_root_path = os.path.join(project_root, adapter_dir)
    project_root_path_abs = os.path.abspath(project_root_path)
    if project_root_path_abs not in candidate_paths:
        candidate_paths.append(project_root_path_abs)
        path_labels.append(f"项目根目录 ({project_root})")
    
    # 2. 当前工作目录
    current_dir_path = os.path.abspath(adapter_dir)
    if current_dir_path not in candidate_paths:
        candidate_paths.append(current_dir_path)
        path_labels.append(f"当前工作目录 ({current_work_dir})")
    
    # 3. ai_service 目录（脚本所在目录）
    script_dir_path = os.path.join(script_dir, adapter_dir)
    script_dir_path_abs = os.path.abspath(script_dir_path)
    if script_dir_path_abs not in candidate_paths:
        candidate_paths.append(script_dir_path_abs)
        path_labels.append(f"脚本所在目录 ({script_dir})")
    
    # 依次检查每个路径
    for path in candidate_paths:
        if os.path.exists(path):
            return path
    
    # 如果都找不到，抛出错误（显示去重后的路径）
    error_msg = f"❌ 找不到模型目录 '{adapter_dir}'\n\n"
    error_msg += "已尝试以下位置：\n"
    for i, (path, label) in enumerate(zip(candidate_paths, path_labels), 1):
        error_msg += f"  {i}. {label}\n     → {path}\n"
    
    error_msg += "\n" + "="*60 + "\n"
    error_msg += "解决方案：\n\n"
    error_msg += "方案1：将模型目录放到以下任一位置：\n"
    for path in candidate_paths[:2]:  # 只显示前两个推荐位置
        error_msg += f"  • {path}\n"
    
    error_msg += "\n方案2：使用环境变量指定模型目录的绝对路径：\n"
    error_msg += "  Windows: set ADAPTER_DIR=D:\\path\\to\\court_debate_model\n"
    error_msg += "  Linux/Mac: export ADAPTER_DIR=/path/to/court_debate_model\n"
    
    error_msg += "\n方案3：在启动脚本中设置（推荐）：\n"
    error_msg += "  编辑 ai_service/start_service.bat，修改 ADAPTER_DIR 环境变量\n"
    
    error_msg += "\n注意：模型目录必须包含 adapter_config.json 文件。\n"
    error_msg += "="*60
    
    raise FileNotFoundError(error_msg)


def update_init_progress(step, message):
    """更新模型初始化进度"""
    global _model_init_status
    with _model_init_lock:
        _model_init_status['progress'] = message
        if step not in _model_init_status['progress_steps']:
            _model_init_status['progress_steps'].append(step)
        logger.info(f"[模型初始化] {message}")


def init_model_async():
    """在后台线程中初始化模型"""
    global _model, _model_lock, _model_init_status
    
    with _model_init_lock:
        if _model is not None:
            _model_init_status['loaded'] = True
            _model_init_status['initializing'] = False
            return
        if _model_init_status['initializing']:
            return
        _model_init_status['initializing'] = True
        _model_init_status['loaded'] = False
        _model_init_status['error'] = None
        _model_init_status['progress'] = ''
        _model_init_status['progress_steps'] = []
    
    def load_model():
        global _model, _model_lock, _model_init_status
        try:
            update_init_progress('start', '正在加载AI模型...')
            
            adapter_dir_env = os.getenv("ADAPTER_DIR", "court_debate_model")
            
            # 解析模型路径
            adapter_dir = resolve_model_path(adapter_dir_env)
            update_init_progress('path_resolved', f'使用模型目录: {adapter_dir}')
            
            load_in_4bit = os.getenv("LOAD_IN_4BIT", "true").lower() == "true"
            gpu_id = int(os.getenv("GPU_ID", "0"))
            
            update_init_progress('config', f'配置: 4bit量化={load_in_4bit}, GPU={gpu_id}')
            
            # 开始加载模型（这一步会花费很长时间，我们添加更多进度点）
            update_init_progress('loading_tokenizer', '正在加载tokenizer...')
            
            _model_lock = True
            _model = CourtDebateModel(
                adapter_dir=adapter_dir,
                load_in_4bit=load_in_4bit,
                gpu_id=gpu_id
            )
            
            # 模型加载完成后，更新进度
            update_init_progress('model_loaded', '模型加载完成，正在验证...')
            
            # 验证模型
            if _model.model is not None and _model.tokenizer is not None:
                update_init_progress('model_verified', '模型验证完成')
            
            update_init_progress('loaded', 'AI模型初始化完成！')
            
            with _model_init_lock:
                _model_init_status['loaded'] = True
                _model_init_status['initializing'] = False
                _model_init_status['error'] = None
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"模型加载失败: {error_msg}")
            with _model_init_lock:
                _model_init_status['error'] = error_msg
                _model_init_status['initializing'] = False
                _model_init_status['loaded'] = False
            _model_lock = False
        finally:
            _model_lock = False
    
    # 在后台线程中加载模型
    thread = threading.Thread(target=load_model, daemon=True)
    thread.start()


def get_model():
    """获取模型实例（单例模式）"""
    global _model, _model_lock
    
    if _model is None and not _model_lock:
        _model_lock = True
        try:
            logger.info("正在加载AI模型...")
            adapter_dir_env = os.getenv("ADAPTER_DIR", "court_debate_model")
            
            # 解析模型路径
            adapter_dir = resolve_model_path(adapter_dir_env)
            logger.info(f"使用模型目录: {adapter_dir}")
            
            load_in_4bit = os.getenv("LOAD_IN_4BIT", "true").lower() == "true"
            gpu_id = int(os.getenv("GPU_ID", "0"))
            
            _model = CourtDebateModel(
                adapter_dir=adapter_dir,
                load_in_4bit=load_in_4bit,
                gpu_id=gpu_id
            )
            logger.info("AI模型加载完成！")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            _model_lock = False
            raise
        finally:
            _model_lock = False
    
    return _model


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'model_loaded': _model is not None
    })


@app.route('/api/model/init', methods=['POST'])
def init_model():
    """初始化模型（后台异步加载）"""
    global _model_init_status
    
    with _model_init_lock:
        if _model is not None:
            return jsonify({
                'success': True,
                'message': '模型已加载',
                'status': 'loaded'
            })
        
        if _model_init_status['initializing']:
            return jsonify({
                'success': True,
                'message': '模型正在初始化中',
                'status': 'initializing'
            })
    
    # 启动后台初始化
    init_model_async()
    
    return jsonify({
        'success': True,
        'message': '模型初始化已启动',
        'status': 'initializing'
    })


@app.route('/api/model/status', methods=['GET'])
def get_model_status():
    """获取模型初始化状态"""
    global _model, _model_init_status
    
    with _model_init_lock:
        status = {
            'loaded': _model is not None or _model_init_status['loaded'],
            'initializing': _model_init_status['initializing'],
            'progress': _model_init_status['progress'],
            'progress_steps': _model_init_status['progress_steps'],
            'error': _model_init_status['error']
        }
    
    return jsonify({
        'success': True,
        'status': status
    })


@app.route('/api/diagnose/external-ai', methods=['GET'])
def diagnose_external_ai():
    """
    诊断外部AI API连接
    用于测试外部API是否可用
    """
    diagnosis = {
        'external_api_url': EXTERNAL_AI_BASE_URL,
        'external_api_model': EXTERNAL_AI_MODEL,
        'api_key_configured': bool(EXTERNAL_AI_API_KEY),
        'api_key_length': len(EXTERNAL_AI_API_KEY) if EXTERNAL_AI_API_KEY else 0,
        'tests': []
    }
    
    # 测试1: 基本连接测试
    test1 = {
        'name': '基本连接测试',
        'status': 'unknown',
        'details': {}
    }
    try:
        import socket
        from urllib.parse import urlparse
        parsed = urlparse(EXTERNAL_AI_BASE_URL)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            test1['status'] = 'success'
            test1['details'] = {'message': f'可以连接到 {host}:{port}'}
        else:
            test1['status'] = 'failed'
            test1['details'] = {'message': f'无法连接到 {host}:{port}', 'error_code': result}
    except Exception as e:
        test1['status'] = 'failed'
        test1['details'] = {'message': '连接测试失败', 'error': str(e)}
    
    diagnosis['tests'].append(test1)
    
    # 测试2: HTTP请求测试
    test2 = {
        'name': 'HTTP请求测试',
        'status': 'unknown',
        'details': {}
    }
    try:
        url = f"{EXTERNAL_AI_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {EXTERNAL_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 发送一个简单的测试请求
        test_payload = {
            "model": EXTERNAL_AI_MODEL,
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        }
        
        response = requests.post(url, headers=headers, json=test_payload, timeout=10)
        
        test2['status'] = 'success' if response.status_code < 500 else 'failed'
        test2['details'] = {
            'http_status': response.status_code,
            'response_headers': dict(response.headers),
            'response_preview': response.text[:200] if response.text else None
        }
        
        if response.status_code == 503:
            test2['details']['message'] = '服务不可用 (503) - 外部API服务可能正在维护或过载'
        elif response.status_code == 401:
            test2['details']['message'] = '认证失败 (401) - API密钥可能无效'
        elif response.status_code == 429:
            test2['details']['message'] = '请求频率过高 (429) - 超过了速率限制'
        elif response.status_code >= 500:
            test2['details']['message'] = f'服务器错误 ({response.status_code})'
        elif response.status_code == 200:
            test2['details']['message'] = 'API可用，连接正常'
        else:
            test2['details']['message'] = f'HTTP状态码: {response.status_code}'
            
    except requests.exceptions.Timeout:
        test2['status'] = 'failed'
        test2['details'] = {'message': '请求超时 - 外部API响应时间过长'}
    except requests.exceptions.ConnectionError as e:
        test2['status'] = 'failed'
        test2['details'] = {'message': '连接错误', 'error': str(e)}
    except Exception as e:
        test2['status'] = 'failed'
        test2['details'] = {'message': '请求失败', 'error': str(e)}
    
    diagnosis['tests'].append(test2)
    
    # 计算总体状态
    all_success = all(test['status'] == 'success' for test in diagnosis['tests'])
    any_failed = any(test['status'] == 'failed' for test in diagnosis['tests'])
    
    if all_success:
        diagnosis['overall_status'] = 'healthy'
        diagnosis['message'] = '外部AI API连接正常'
    elif any_failed:
        diagnosis['overall_status'] = 'unhealthy'
        diagnosis['message'] = '外部AI API连接存在问题，请查看详细测试结果'
    else:
        diagnosis['overall_status'] = 'unknown'
        diagnosis['message'] = '无法确定外部AI API状态'
    
    return jsonify(diagnosis)


@app.route('/api/generate', methods=['POST'])
def generate():
    """生成单次回复"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_new_tokens', 8192)  # 默认值改为8192，基本无限制
        temperature = data.get('temperature', 0.6)
        top_p = data.get('top_p', 0.9)
        system_prompt = data.get('system_prompt')
        assistant_role = data.get('assistant_role')
        
        if not prompt:
            return jsonify({'error': 'prompt参数不能为空'}), 400
        
        model = get_model()
        if model is None:
            return jsonify({'error': '模型未加载'}), 500
        
        response = model.generate(
            prompt=prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            system_prompt=system_prompt,
            assistant_role=assistant_role
        )
        
        return jsonify({
            'response': response,
            'success': True
        })
    
    except Exception as e:
        logger.error(f"生成失败: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """对话生成（带历史）"""
    try:
        data = request.json
        messages = data.get('messages', [])
        max_tokens = data.get('max_new_tokens', 8192)  # 默认值改为8192，基本无限制
        temperature = data.get('temperature', 0.6)
        top_p = data.get('top_p', 0.9)
        system_prompt = data.get('system_prompt')
        assistant_role = data.get('assistant_role')
        
        if not messages:
            return jsonify({'error': 'messages参数不能为空'}), 400
        
        model = get_model()
        if model is None:
            return jsonify({'error': '模型未加载'}), 500
        
        response = model.chat(
            messages=messages,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            system_prompt=system_prompt,
            assistant_role=assistant_role
        )
        
        return jsonify({
            'response': response,
            'success': True
        })
    
    except Exception as e:
        logger.error(f"对话生成失败: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/debate/generate', methods=['POST'])
def debate_generate():
    """
    法庭辩论生成
    支持两种输入格式：
    1. 训练数据格式（推荐）：
       {
         "agent_role": "审判员",  // 当前要回复的角色
         "background": "...",     // 案件背景
         "context": "...",        // 对话历史（用\n分隔）
         "role_to_reply": "辩护人", // 要回复的角色
         "instruction": "..."     // 角色指令
       }
    2. 旧格式（向后兼容）：
       {
         "user_identity": "plaintiff",
         "current_role": "judge",
         "messages": [...],
         "judge_type": "neutral",
         "case_description": "..."
       }
    """
    try:
        data = request.json
        
        # 检查是否为训练数据格式
        if 'agent_role' in data or 'context' in data:
            # 使用训练数据格式
            return debate_generate_training_format(data)
        else:
            # 使用旧格式（向后兼容）
            return debate_generate_legacy_format(data)
    
    except Exception as e:
        logger.error(f"辩论生成失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


def debate_generate_training_format(data):
    """
    使用训练数据格式生成回复
    
    输入字段说明：
    - agent_role: 当前AI扮演的角色（如"审判员"、"公诉人"、"辩护人"等）
    - background: 案件背景（前面保存的案件描述）
    - context: 上下文（对话历史，用\n分隔）
    - instruction: 角色指令（包含诉讼策略、法官类型等）
    - role_to_reply: 要回复的角色（可选，默认与agent_role相同）
    """
    agent_role = data.get('agent_role')  # 当前AI扮演的角色
    background = data.get('background', '')  # 案件背景（从前面保存的案件描述获取）
    context = data.get('context', '')  # 上下文（对话历史，用\n分隔）
    role_to_reply = data.get('role_to_reply', agent_role)  # 要回复的角色（可选）
    instruction = data.get('instruction', '')  # 角色指令（包含诉讼策略、法官类型等）
    
    if not agent_role:
        return jsonify({'error': 'agent_role参数不能为空'}), 400
    
    logger.info(f"[训练格式] agent_role={agent_role}, background长度={len(background)}, context长度={len(context)}, instruction长度={len(instruction)}")
    if instruction:
        logger.info(f"[训练格式] instruction预览: {instruction[:200]}...")
    
    model = get_model()
    if model is None:
        return jsonify({'error': '模型未加载'}), 500
    
    # 构建系统提示词（基于训练数据格式）
    system_prompt = build_system_prompt_from_training_format(
        agent_role=agent_role,
        background=background,
        instruction=instruction
    )
    logger.info(f"[训练格式] 系统提示词长度: {len(system_prompt)}")
    
    # 将context转换为消息格式
    formatted_messages = format_context_to_messages(context)
    logger.info(f"[训练格式] 转换后的消息数量: {len(formatted_messages)}")
    if formatted_messages:
        logger.info(f"[训练格式] 第一条消息预览: {formatted_messages[0].get('content', '')[:100]}...")
        logger.info(f"[训练格式] 最后一条消息预览: {formatted_messages[-1].get('content', '')[:100]}...")
    
    # 生成回复（移除max_new_tokens限制，使用很大的值确保生成完整内容）
    response = model.chat(
        messages=formatted_messages,
        max_new_tokens=8192,  # 设置为很大的值，基本无限制
        temperature=0.6,
        top_p=0.9,
        system_prompt=system_prompt,
        assistant_role=agent_role
    )
    
    logger.info(f"[训练格式] 生成回复长度: {len(response)}")
    logger.info(f"[训练格式] 生成回复预览: {response[:200]}...")
    
    return jsonify({
        'code': 200,
        'data': response,
        'role': agent_role,
        'success': True
    })


def debate_generate_legacy_format(data):
    """使用旧格式生成回复（向后兼容）"""
    user_identity = data.get('user_identity')  # 'plaintiff' 或 'defendant'
    current_role = data.get('current_role')  # 'judge', 'plaintiff', 'defendant'
    messages = data.get('messages', [])  # 对话历史
    judge_type = data.get('judge_type', 'neutral')  # 法官类型
    case_description = data.get('case_description', '')  # 案件描述（现在可能包含完整的background）
    check_mode = data.get('checkMode', False)  # 是否为判断模式
    prompt = data.get('prompt', '')  # 特殊提示词（用于判断模式）
    is_first_judge_speech = data.get('isFirstJudgeSpeech', False)  # 是否为首次法官发言
    
    if not user_identity or not current_role:
        return jsonify({'error': 'user_identity和current_role参数不能为空'}), 400
    
    model = get_model()
    if model is None:
        return jsonify({'error': '模型未加载'}), 500
    
    # 构建系统提示词
    # case_description 现在可能包含完整的background（身份信息、文件列表、案件描述、诉讼策略等）
    system_prompt = build_system_prompt(user_identity, current_role, judge_type, case_description)
    assistant_role = get_assistant_role_name(current_role)
    
    # 构建消息历史
    formatted_messages = format_messages_for_ai(messages)
    
    # 如果是判断模式且有特殊提示词，添加提示词
    if check_mode and prompt:
        formatted_messages.append({
            'role': 'user',
            'content': prompt
        })
    
    # 生成回复（移除max_new_tokens限制，使用很大的值确保生成完整内容）
    response = model.chat(
        messages=formatted_messages,
        max_new_tokens=8192,  # 设置为很大的值，基本无限制
        temperature=0.6,
        top_p=0.9,
        system_prompt=system_prompt,
        assistant_role=assistant_role
    )
    
    logger.info(f"[旧格式] 生成回复长度: {len(response)}")
    logger.info(f"[旧格式] 生成回复预览: {response[:200]}...")
    
    return jsonify({
        'code': 200,
        'data': response,
        'role': current_role,
        'success': True
    })


def build_system_prompt_from_training_format(agent_role, background, instruction):
    """
    根据训练数据格式构建系统提示词
    
    Args:
        agent_role: 当前AI扮演的角色（如"审判员"、"公诉人"、"辩护人"等）
        background: 案件背景（前面保存的案件描述）
        instruction: 角色指令（包含诉讼策略、法官类型等）
    """
    base_prompt = "你是一位专业的法律从业者，需要根据角色定位参与法庭辩论。\n\n"
    
    # 1. 添加角色定义
    role_definitions = {
        '审判员': '角色：审判员\n职责：主持庭审，引导辩论，确保程序公正',
        '公诉人': '角色：公诉人\n职责：代表国家行使公诉权，指控犯罪事实，出示并质证证据',
        '辩护人': '角色：辩护人\n职责：维护被告人的合法权益，针对指控提出辩护意见和反驳',
        '原告': '角色：原告代理律师\n职责：代表原告维护权益，提出诉讼请求，提供证据和理由',
        '被告': '角色：被告代理律师\n职责：代表被告进行辩护，反驳原告指控，维护被告权益'
    }
    
    role_def = role_definitions.get(agent_role, f'角色：{agent_role}')
    base_prompt += f"【角色定义】\n{role_def}\n\n"
    
    # 2. 添加案件背景（从前面保存的案件描述获取）
    if background:
        base_prompt += f"【案件背景】\n{background}\n\n"
    
    # 3. 添加角色指令（instruction字段，包含诉讼策略、法官类型等）
    # 这是最重要的部分，包含了具体的策略指导和角色特征
    if instruction:
        base_prompt += f"【角色指令与策略】\n{instruction}\n\n"
    else:
        # 如果没有提供instruction，使用默认指令
        default_instructions = {
            '审判员': '请严格按照以下要求：\n1. 保持中立、客观、公正的立场\n2. 引导庭审程序有序进行，控制庭审节奏\n3. 对争议焦点进行归纳和总结\n4. 确保各方充分表达意见，维护庭审秩序\n5. 基于事实和法律进行判断，不偏不倚',
            '公诉人': '请严格按照以下要求：\n1. 代表国家行使公诉权，指控犯罪事实\n2. 出示并质证证据，证明犯罪构成要件\n3. 回应辩方意见，维护指控的合法性\n4. 围绕争议焦点组织举证质证\n5. 强调主客观要件与因果关系，突出量刑情节',
            '辩护人': '请严格按照以下要求：\n1. 维护被告人的合法权益\n2. 针对指控提出辩护意见和反驳\n3. 提出有利于被告人的证据和事实\n4. 质疑控方证据的合法性、真实性、关联性\n5. 为被告人争取从轻、减轻或免除处罚',
            '原告': '请严格按照以下要求：\n1. 代表原告维护权益，提出诉讼请求\n2. 提供证据和理由支持诉讼请求\n3. 回应被告的答辩意见\n4. 围绕争议焦点组织举证质证\n5. 强调事实和法律依据',
            '被告': '请严格按照以下要求：\n1. 代表被告进行辩护，反驳原告指控\n2. 提出有利于被告的证据和事实\n3. 质疑原告证据的合法性、真实性、关联性\n4. 维护被告权益\n5. 争取从轻、减轻或免除责任'
        }
        default_instruction = default_instructions.get(agent_role, '请根据你的角色定位，在法庭辩论中保持专业严谨。')
        base_prompt += f"【角色指令与策略】\n{default_instruction}\n\n"
    
    # 4. 添加通用要求
    base_prompt += "【通用要求】\n"
    base_prompt += "请根据你的角色定位，在法庭辩论中：\n"
    base_prompt += "1. 根据对话历史理解当前辩论阶段和焦点\n"
    base_prompt += "2. 根据角色标记（审判员/公诉人/辩护人/原告/被告）切换相应的语言风格\n"
    base_prompt += "3. 遵循法庭辩论的逻辑顺序和程序规范\n"
    base_prompt += "4. 基于事实和法律条文进行专业辩论"
    
    return base_prompt


def format_context_to_messages(context):
    """
    将训练数据格式的context（用\n分隔的对话）转换为消息格式
    
    输入格式：
    "审判员: 现在开庭...\n公诉人: 根据起诉书...\n辩护人: 我方认为..."
    或
    "审判员：现在开庭...\n公诉人：根据起诉书...\n辩护人：我方认为..."
    
    输出格式：
    [
        {"role": "user", "content": "审判员：现在开庭..."},
        {"role": "assistant", "content": "公诉人：根据起诉书..."},
        {"role": "user", "content": "辩护人：我方认为..."}
    ]
    """
    if not context:
        return []
    
    messages = []
    lines = context.strip().split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # 解析角色和内容（支持英文冒号:和中文冒号：）
        role_name = ''
        content = line
        
        # 优先匹配中文冒号（更常见）
        if '：' in line:
            parts = line.split('：', 1)
            role_name = parts[0].strip()
            content = parts[1].strip() if len(parts) > 1 else ''
        elif ':' in line:
            # 支持英文冒号（训练数据格式）
            parts = line.split(':', 1)
            role_name = parts[0].strip()
            content = parts[1].strip() if len(parts) > 1 else ''
        
        # 确定消息角色（交替使用user和assistant）
        # 第一条消息通常是user，后续交替
        if i == 0:
            msg_role = 'user'
        else:
            # 根据前一条消息的角色决定
            prev_role = messages[-1].get('role', 'user')
            msg_role = 'assistant' if prev_role == 'user' else 'user'
        
        # 构建消息内容（统一使用中文冒号）
        if role_name:
            msg_content = f"{role_name}：{content}"
        else:
            msg_content = content
        
        messages.append({
            'role': msg_role,
            'content': msg_content
        })
    
    return messages


def build_system_prompt(user_identity, current_role, judge_type, case_description):
    """构建系统提示词
    case_description 现在可能包含完整的background（身份信息、文件列表、案件描述、诉讼策略等）
    """
    base_prompt = "你是一位专业的法律从业者，需要根据角色定位参与法庭辩论。\n\n"
    
    if current_role == 'judge':
        # 法官角色 - 法官类型会加入角色提示词中
        judge_prompts = {
            'professional': '你是一位专业型法官，讲话简洁，业务熟练，判决果断。',
            'strong': '你是一位强势型法官，专业能力出众，细节能力强。',
            'partial-plaintiff': '你是一位偏袒型法官，习惯对原告宽容。',
            'partial-defendant': '你是一位偏袒型法官，习惯对被告宽容。',
            'neutral': '你是一位中立型法官，保持中立，注重程序公正。'
        }
        role_prompt = judge_prompts.get(judge_type, judge_prompts['neutral'])
        base_prompt += f"{role_prompt}\n\n"
        base_prompt += f"角色定义：\n- 角色：审判员\n- 职责：主持庭审，引导辩论，确保程序公正\n\n"
    elif current_role == 'plaintiff':
        # 原告律师角色
        base_prompt += f"角色定义：\n- 角色：原告代理律师\n- 职责：代表原告维护权益，提出诉讼请求，提供证据和理由\n\n"
    elif current_role == 'defendant':
        # 被告律师角色
        base_prompt += f"角色定义：\n- 角色：被告代理律师\n- 职责：代表被告进行辩护，反驳原告指控，维护被告权益\n\n"
    
    # case_description 现在包含完整的background（身份信息、文件列表、案件描述、诉讼策略等）
    # 这些信息在每次AI回答时都要能看到
    if case_description:
        base_prompt += f"{case_description}\n\n"
    
    base_prompt += "请根据你的角色定位，在法庭辩论中：\n"
    base_prompt += "1. 根据对话历史理解当前辩论阶段和焦点\n"
    base_prompt += "2. 根据角色标记（审判员/原告/被告）切换相应的语言风格\n"
    base_prompt += "3. 遵循法庭辩论的逻辑顺序和程序规范\n"
    base_prompt += "4. 基于事实和法律条文进行专业辩论"
    
    return base_prompt


def get_assistant_role_name(role):
    """获取助手角色名称"""
    role_map = {
        'judge': '审判员',
        'plaintiff': '原告',
        'defendant': '被告'
    }
    return role_map.get(role, '审判员')


def format_messages_for_ai(messages):
    """将前端消息格式转换为AI需要的格式"""
    formatted = []
    for msg in messages:
        role = msg.get('role')
        text = msg.get('text', '')
        name = msg.get('name', '')
        
        # 转换为AI格式
        if role == 'judge':
            ai_role = 'user'
            content = f"审判员：{text}"
        elif role == 'plaintiff':
            ai_role = 'user' if len(formatted) == 0 or formatted[-1].get('role') != 'user' else 'assistant'
            content = f"原告：{text}"
        elif role == 'defendant':
            ai_role = 'user' if len(formatted) == 0 or formatted[-1].get('role') != 'user' else 'assistant'
            content = f"被告：{text}"
        else:
            continue
        
        formatted.append({
            'role': ai_role,
            'content': content
        })
    
    return formatted


def call_external_ai(prompt, system_prompt=None, max_tokens=2000, max_retries=3):
    """
    调用外部AI API（OpenAI兼容接口）
    
    Args:
        prompt: 用户提示词
        system_prompt: 系统提示词（可选）
        max_tokens: 最大生成token数
        max_retries: 最大重试次数（默认3次）
    
    Returns:
        AI生成的文本
    """
    url = f"{EXTERNAL_AI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {EXTERNAL_AI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    payload = {
        "model": EXTERNAL_AI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    # 记录请求详情
    prompt_length = len(prompt)
    system_prompt_length = len(system_prompt) if system_prompt else 0
    total_messages_length = sum(len(str(msg.get("content", ""))) for msg in messages)
    
    logger.info("=" * 60)
    logger.info("调用外部AI API - 请求详情")
    logger.info("=" * 60)
    logger.info(f"URL: {url}")
    logger.info(f"模型: {EXTERNAL_AI_MODEL}")
    logger.info(f"用户提示词长度: {prompt_length} 字符")
    logger.info(f"系统提示词长度: {system_prompt_length} 字符")
    logger.info(f"消息总数: {len(messages)}")
    logger.info(f"总消息内容长度: {total_messages_length} 字符")
    logger.info(f"最大token数: {max_tokens}")
    logger.info(f"最大重试次数: {max_retries}")
    logger.info(f"API密钥前缀: {EXTERNAL_AI_API_KEY[:10]}...{EXTERNAL_AI_API_KEY[-4:] if len(EXTERNAL_AI_API_KEY) > 14 else ''}")
    
    # 重试机制
    import time
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                # 指数退避：第1次重试等待2秒，第2次等待4秒，第3次等待8秒
                wait_time = 2 ** attempt
                logger.info(f"等待 {wait_time} 秒后重试（第 {attempt + 1}/{max_retries} 次尝试）...")
                time.sleep(wait_time)
            
            # 增加超时时间
            response = requests.post(
                url, 
                headers=headers, 
                json=payload, 
                timeout=90,  # 增加超时时间到90秒
                verify=True  # 保持SSL验证，但如果遇到SSL错误，会在异常处理中提供建议
            )
            
            # 记录响应详情
            status_code = response.status_code
            response_headers = dict(response.headers)
            
            logger.info("=" * 60)
            logger.info("外部AI API - 响应详情")
            logger.info("=" * 60)
            logger.info(f"HTTP状态码: {status_code}")
            logger.info(f"响应头: {response_headers}")
            
            # 尝试读取和解析响应体
            api_error_info = None
            try:
                response_text = response.text
                response_length = len(response_text)
                logger.info(f"响应体长度: {response_length} 字符")
                
                # 如果响应体不太长，记录完整内容；否则只记录前500字符
                if response_length < 1000:
                    logger.info(f"响应体内容: {response_text}")
                else:
                    logger.info(f"响应体预览（前500字符）: {response_text[:500]}...")
                
                # 尝试解析JSON
                try:
                    response_json = response.json()
                    logger.info(f"响应JSON解析成功")
                    if "error" in response_json:
                        api_error_info = response_json.get('error')
                        if isinstance(api_error_info, dict):
                            error_code = api_error_info.get('code', '')
                            error_message = api_error_info.get('message', '')
                            error_type = api_error_info.get('type', '')
                            
                            logger.error("=" * 60)
                            logger.error("❌ API返回错误详情")
                            logger.error("=" * 60)
                            logger.error(f"错误代码: {error_code}")
                            logger.error(f"错误类型: {error_type}")
                            logger.error(f"错误消息: {error_message}")
                            
                            # 针对特定错误提供详细诊断
                            if error_code == 'model_not_found':
                                logger.error("")
                                logger.error("🔍 模型未找到错误分析：")
                                logger.error(f"  请求的模型: {EXTERNAL_AI_MODEL}")
                                logger.error(f"  错误消息: {error_message}")
                                logger.error("")
                                logger.error("可能的原因和解决方案：")
                                logger.error("1. 模型名称不正确")
                                logger.error("   - 检查API服务商文档，确认正确的模型名称")
                                logger.error("   - 可能需要的名称：gpt-4o-mini, gpt-4o-mini-2024-08-06, gpt-4o-mini-2024-07-18 等")
                                logger.error("")
                                logger.error("2. 模型在指定分组下不可用")
                                logger.error("   - 错误消息提到'分组 default 下模型无可用渠道'")
                                logger.error("   - 可能需要：")
                                logger.error("     a) 使用不同的分组名称")
                                logger.error("     b) 在API请求中指定分组参数")
                                logger.error("     c) 联系API服务商配置模型渠道")
                                logger.error("")
                                logger.error("3. API密钥权限问题")
                                logger.error("   - 当前API密钥可能没有权限使用该模型")
                                logger.error("   - 检查API密钥对应的账户是否有该模型的访问权限")
                                logger.error("   - 可能需要升级账户或购买模型访问权限")
                                logger.error("")
                                logger.error("4. 模型暂时不可用")
                                logger.error("   - 该模型可能暂时下架或维护中")
                                logger.error("   - 尝试使用其他可用的模型（如 gpt-3.5-turbo）")
                                logger.error("=" * 60)
                            elif error_code == 'invalid_api_key':
                                logger.error("")
                                logger.error("🔍 API密钥无效")
                                logger.error("   - 检查API密钥是否正确")
                                logger.error("   - 确认API密钥是否已过期")
                                logger.error("   - 验证API密钥是否有权限访问该模型")
                                logger.error("=" * 60)
                            elif error_code == 'insufficient_quota':
                                logger.error("")
                                logger.error("🔍 配额不足")
                                logger.error("   - 账户余额不足")
                                logger.error("   - 需要充值或升级账户")
                                logger.error("=" * 60)
                        else:
                            logger.error(f"API返回错误信息: {api_error_info}")
                except:
                    logger.warning("响应体不是有效的JSON格式")
            except Exception as e:
                logger.warning(f"读取响应体失败: {e}")
            
            # 检查HTTP状态码
            if status_code == 503:
                logger.error("=" * 60)
                logger.error("❌ 503 Service Unavailable - 服务不可用")
                logger.error("=" * 60)
                
                # 如果API返回了具体的错误信息，优先显示
                if api_error_info and isinstance(api_error_info, dict):
                    error_code = api_error_info.get('code', '')
                    if error_code == 'model_not_found':
                        # model_not_found错误已经在上面详细处理了，这里只显示简要提示
                        logger.error("注意：虽然HTTP状态码是503，但实际错误是模型未找到")
                        logger.error("请查看上面的详细错误分析")
                    else:
                        logger.error(f"API错误代码: {error_code}")
                        logger.error(f"API错误消息: {api_error_info.get('message', '')}")
                else:
                    logger.error("可能的原因：")
                    logger.error("1. 外部API服务正在维护或升级")
                    logger.error("2. 服务器过载，无法处理请求")
                    logger.error("3. 网络连接问题或DNS解析失败")
                    logger.error("4. API服务提供商临时故障")
                    logger.error("5. 请求频率过高，被限流")
                    logger.error("")
                    logger.error("诊断建议：")
                    logger.error("1. 检查外部API服务状态页面（如果有）")
                    logger.error("2. 使用curl或postman直接测试API端点")
                    logger.error("3. 检查网络连接和DNS解析")
                    logger.error("4. 等待一段时间后重试")
                    logger.error("5. 联系API服务提供商确认服务状态")
                logger.error("=" * 60)
            elif status_code == 401:
                logger.error("❌ 401 Unauthorized - 认证失败")
                logger.error("可能的原因：API密钥无效或过期")
            elif status_code == 429:
                logger.error("❌ 429 Too Many Requests - 请求频率过高")
                logger.error("可能的原因：超过了API的速率限制")
            elif status_code >= 500:
                logger.error(f"❌ {status_code} Server Error - 服务器错误")
                logger.error("可能的原因：外部API服务器内部错误")
            
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.info(f"✅ 外部AI API调用成功，生成了 {len(content)} 个字符")
                return content
            else:
                logger.error(f"❌ 外部AI API返回格式异常: {result}")
                raise ValueError("外部AI API返回格式异常")
    
        except requests.exceptions.Timeout as e:
            last_exception = e
            error_str = str(e)
            logger.error("=" * 60)
            logger.error(f"❌ 请求超时（第 {attempt + 1}/{max_retries} 次尝试）")
            logger.error("=" * 60)
            logger.error(f"错误详情: {error_str}")
            logger.error("可能的原因：")
            logger.error("1. 网络连接慢或不稳定")
            logger.error("2. 外部API响应时间过长")
            logger.error("3. 请求内容过大，处理时间过长")
            logger.error("=" * 60)
            
            # 如果是最后一次尝试，抛出异常
            if attempt == max_retries - 1:
                raise RuntimeError(f"调用外部AI API超时（已重试{max_retries}次）: {error_str}")
            # 否则继续重试
            continue
    
        except requests.exceptions.SSLError as e:
            last_exception = e
            error_str = str(e)
            logger.error("=" * 60)
            logger.error(f"❌ SSL连接错误（第 {attempt + 1}/{max_retries} 次尝试）")
            logger.error("=" * 60)
            logger.error(f"错误详情: {error_str}")
            logger.error("可能的原因：")
            logger.error("1. SSL证书验证失败")
            logger.error("2. SSL握手过程中连接意外中断")
            logger.error("3. 服务器SSL配置问题")
            logger.error("4. 网络不稳定导致SSL连接中断")
            logger.error("5. 防火墙或代理干扰SSL连接")
            logger.error("")
            logger.error("诊断建议：")
            logger.error("1. 检查网络连接是否稳定")
            logger.error("2. 检查防火墙和代理设置")
            logger.error("3. 尝试使用curl测试API端点")
            logger.error("4. 联系API服务提供商确认服务状态")
            logger.error("=" * 60)
            
            # 如果是最后一次尝试，抛出异常
            if attempt == max_retries - 1:
                raise RuntimeError(f"无法连接到外部AI API（SSL错误，已重试{max_retries}次）: {error_str}")
            # 否则继续重试
            continue
            
        except requests.exceptions.ConnectionError as e:
            last_exception = e
            error_str = str(e)
            logger.error("=" * 60)
            logger.error(f"❌ 连接错误（第 {attempt + 1}/{max_retries} 次尝试）")
            logger.error("=" * 60)
            logger.error(f"错误详情: {error_str}")
            logger.error("可能的原因：")
            logger.error("1. 无法连接到外部API服务器")
            logger.error("2. DNS解析失败")
            logger.error("3. 防火墙或代理阻止连接")
            logger.error("4. 外部API服务器已关闭")
            logger.error("=" * 60)
            
            # 如果是最后一次尝试，抛出异常
            if attempt == max_retries - 1:
                raise RuntimeError(f"无法连接到外部AI API（已重试{max_retries}次）: {error_str}")
            # 否则继续重试
            continue
    
        except requests.exceptions.HTTPError as e:
            # HTTP错误（如500、503等）通常不需要重试，直接抛出
            error_str = str(e)
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            if status_code:
                logger.error(f"❌ HTTP错误: {error_str} (状态码: {status_code})")
                raise RuntimeError(f"调用外部AI API失败: HTTP {status_code} - {error_str}")
            else:
                logger.error(f"❌ HTTP错误: {error_str}")
                raise RuntimeError(f"调用外部AI API失败: {error_str}")
        
        except requests.exceptions.RequestException as e:
            last_exception = e
            error_str = str(e)
            logger.error("=" * 60)
            logger.error(f"❌ 请求异常（第 {attempt + 1}/{max_retries} 次尝试）")
            logger.error("=" * 60)
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误详情: {error_str}")
            logger.error("=" * 60)
            
            # 如果是最后一次尝试，抛出异常
            if attempt == max_retries - 1:
                raise RuntimeError(f"调用外部AI API失败（已重试{max_retries}次）: {error_str}")
            # 否则继续重试
            continue
        
        except Exception as e:
            # 其他异常（如JSON解析错误等）通常不需要重试
            logger.error("=" * 60)
            logger.error("❌ 处理外部AI API响应失败")
            logger.error("=" * 60)
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误详情: {e}")
            import traceback
            logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
            logger.error("=" * 60)
            raise RuntimeError(f"处理外部AI API响应失败: {str(e)}")
    
    # 如果所有重试都失败了，抛出最后一个异常
    if last_exception:
        raise RuntimeError(f"调用外部AI API失败（已重试{max_retries}次）: {str(last_exception)}")


@app.route('/api/case/summarize', methods=['POST'])
def summarize_case():
    """
    案件资料自动总结
    根据上传的文件信息生成案件描述
    支持文件内容读取
    """
    try:
        data = request.json
        file_names = data.get('file_names', [])
        file_contents = data.get('file_contents', [])  # 文件内容列表
        identity = data.get('identity', '')  # 'plaintiff' 或 'defendant'
        
        if not file_names:
            return jsonify({'error': 'file_names参数不能为空'}), 400
        
        # 构建提示词
        identity_text = "原告" if identity == "plaintiff" else "被告"
        
        # 如果有文件内容，使用文件内容；否则只使用文件名
        if file_contents and len(file_contents) > 0:
            # 使用文件内容
            files_info = "\n\n".join(file_contents)
            user_prompt = f"""请根据以下{identity_text}上传的案件文件内容，生成一份详细的案件描述：

{files_info}

重要提示：
1. 如果文件是试题、案例题、练习题、竞赛题目等，请提取试题中描述的实际案件信息，而不是总结试题本身（如"这是XX竞赛的试题"这类元信息）。
2. 忽略文件的标题、注意事项、提交要求等非案件事实的内容，专注于提取案件本身的信息。
3. 提取案件中的当事人、事件经过、时间、地点、争议焦点等实际案件要素。
4. 如果文件中包含多个案件，请总结所有案件；如果只有一个案件，请详细总结该案件。

请仔细分析上述文件内容，提取关键信息，生成一份专业的案件描述。"""
        else:
            # 只有文件名，使用文件名列表
            file_list_text = "\n".join([f"- {name}" for name in file_names])
            user_prompt = f"""请根据以下{identity_text}上传的案件文件，生成一份详细的案件描述：

文件列表：
{file_list_text}

请基于这些文件信息，生成一份专业的案件描述。如果无法从文件名推断具体内容，请根据常见的案件类型和文件类型进行合理推测，生成一份符合法律规范的案件描述。"""
        
        system_prompt = """你是一位专业的法律助理，擅长分析和总结案件资料。请根据提供的文件信息，生成一份结构化的案件描述。

重要原则：
1. 如果文件是试题、案例题、练习题等，必须提取试题中描述的实际案件信息，而不是总结试题的格式、要求等元信息。
2. 忽略文件的标题、注意事项、提交要求、格式要求等非案件事实的内容。
3. 专注于提取文件中描述的实际案件：当事人姓名、事件经过、时间、地点、争议事实等。

要求：
1. 分析案件的基本情况（当事人、案由、时间等）
2. 识别争议焦点
3. 列出相关法条（根据案件类型，如刑事案件、民事案件等）
4. 提取案件关键要素（当事人关系、事件经过、时间节点、地点、证据等）
5. 使用清晰的结构和专业的法律术语

输出格式：
案件基本情况：
[案件基本情况描述，包括当事人、案由、时间、地点等]

争议焦点：
1. [焦点1]
2. [焦点2]
...

相关法条：
[相关法条引用，根据案件类型选择，如刑法、民法、诉讼法等]

案件要素：
- [要素1]
- [要素2]
..."""
        
        # 调用外部AI API
        summary = call_external_ai(user_prompt, system_prompt, max_tokens=2000)
        
        return jsonify({
            'summary': summary,
            'success': True
        })
    
    except Exception as e:
        logger.error(f"案件总结失败: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/verdict/generate', methods=['POST'])
def generate_verdict():
    """
    庭后宣判 - 生成判决书
    根据案件信息和庭审对话历史生成判决书
    """
    try:
        data = request.json
        case_description = data.get('case_description', '')
        messages = data.get('messages', [])  # 庭审对话历史
        identity = data.get('identity', '')  # 用户身份
        
        if not case_description:
            return jsonify({'error': 'case_description参数不能为空'}), 400
        
        # 构建庭审对话摘要
        dialogue_summary = ""
        if messages:
            dialogue_summary = "\n".join([
                f"{msg.get('name', '')}：{msg.get('text', '')}" 
                for msg in messages 
                if msg.get('text')
            ])
        
        system_prompt = """你是一位专业的法官，需要根据案件信息和庭审对话历史，生成一份完整的民事判决书。

判决书应包含以下部分：
1. 案件基本信息（当事人信息、案由、案件编号、审理法院、审理时间等）
2. 审理经过（起诉时间和事实、审理过程概述、当事人主要争议点）
3. 当事人诉讼请求和答辩（原告诉讼请求、被告的答辩意见、争议的主要问题）
4. 本院查明的事实（基于案件描述和庭审对话）
5. 本院认为（法律适用分析、对争议问题的法律判断、责任认定和理由）

要求：
- 使用正式的法律文书格式
- 语言严谨、专业
- 基于提供的案件信息和庭审对话进行合理推断
- 判决书应完整、逻辑清晰"""
        
        user_prompt = f"""请根据以下案件信息和庭审对话，生成一份完整的民事判决书：

案件描述：
{case_description}

庭审对话历史：
{dialogue_summary if dialogue_summary else "（无详细对话记录）"}

请生成一份完整的民事判决书，包含所有必要的部分。"""
        
        # 调用外部AI API
        verdict = call_external_ai(user_prompt, system_prompt, max_tokens=4000)
        
        return jsonify({
            'verdict': verdict,
            'success': True
        })
    
    except Exception as e:
        logger.error(f"判决书生成失败: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"启动AI服务，端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

