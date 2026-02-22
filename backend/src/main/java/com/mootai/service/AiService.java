package com.mootai.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class AiService {
    
    private final RestTemplate restTemplate;
    
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Value("${ai.service.url:http://localhost:5000}")
    private String aiServiceUrl;
    
    /**
     * 生成法庭辩论回复
     * 将旧格式转换为训练数据格式
     * 
     * @param userIdentity 用户身份（plaintiff 或 defendant）
     * @param currentRole 当前角色（judge, plaintiff, defendant）
     * @param messages 对话历史
     * @param judgeType 法官类型
     * @param caseDescription 案件描述
     * @return AI生成的回复
     */
    public String generateDebateResponse(
            String userIdentity,
            String currentRole,
            List<Map<String, Object>> messages,
            String judgeType,
            String caseDescription
    ) {
        try {
            String url = aiServiceUrl + "/api/debate/generate";
            
            // 转换为训练数据格式
            Map<String, Object> requestBody = convertToTrainingFormat(
                    userIdentity, currentRole, messages, judgeType, caseDescription
            );
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            // 输出详细的输入参数日志
            log.info("========== 调用AI服务：生成法庭辩论回复 ==========");
            log.info("URL: {}", url);
            log.info("用户身份: {}", userIdentity);
            log.info("当前角色: {}", currentRole);
            log.info("法官类型: {}", judgeType);
            log.info("案件描述长度: {} 字符", caseDescription != null ? caseDescription.length() : 0);
            log.info("对话历史消息数: {}", messages != null ? messages.size() : 0);
            if (messages != null && !messages.isEmpty()) {
                log.info("对话历史预览（前3条）:");
                for (int i = 0; i < Math.min(3, messages.size()); i++) {
                    Map<String, Object> msg = messages.get(i);
                    Object textObj = msg.get("text");
                    String textPreview = "";
                    if (textObj != null) {
                        String text = textObj.toString();
                        if (text.length() > 100) {
                            textPreview = text.substring(0, 100) + "...";
                        } else {
                            textPreview = text;
                        }
                    }
                    log.info("  [{}] {}: {}", i + 1, msg.get("name"), textPreview);
                }
            }
            log.info("转换后的请求体（训练数据格式）: {}", objectMapper.writeValueAsString(requestBody));
            log.info("================================================");
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                Boolean success = (Boolean) body.get("success");
                if (Boolean.TRUE.equals(success)) {
                    String aiResponse = (String) body.get("response");
                    log.debug("AI服务返回: {}", aiResponse);
                    return aiResponse;
                } else {
                    String error = (String) body.get("error");
                    log.error("AI服务返回错误: {}", error);
                    throw new RuntimeException("AI服务错误: " + error);
                }
            } else {
                log.error("AI服务调用失败，状态码: {}", response.getStatusCode());
                throw new RuntimeException("AI服务调用失败");
            }
        } catch (Exception e) {
            log.error("调用AI服务异常", e);
            throw new RuntimeException("AI服务调用异常: " + e.getMessage(), e);
        }
    }
    
    /**
     * 将旧格式转换为训练数据格式
     * 
     * @param userIdentity 用户身份
     * @param currentRole 当前角色
     * @param messages 对话历史
     * @param judgeType 法官类型
     * @param caseDescription 案件描述（现在包含完整的庭前准备资料）
     * @return 训练数据格式的请求体
     */
    private Map<String, Object> convertToTrainingFormat(
            String userIdentity,
            String currentRole,
            List<Map<String, Object>> messages,
            String judgeType,
            String caseDescription
    ) {
        Map<String, Object> requestBody = new HashMap<>();
        
        // 1. 转换 agent_role（当前AI扮演的角色）
        String agentRole = convertRoleToChinese(currentRole);
        requestBody.put("agent_role", agentRole);
        
        // 2. 转换 background（案件背景，现在包含所有庭前准备资料）
        // caseDescription 参数现在已经是完整的background，包含：
        // - 身份信息
        // - 上传文件列表
        // - 案件描述
        // - 诉讼策略
        String background = caseDescription != null ? caseDescription : "";
        requestBody.put("background", background);
        
        // 3. 转换 context（对话历史，用\n分隔）
        String context = convertMessagesToContext(messages);
        requestBody.put("context", context);
        
        // 4. 转换 instruction（角色指令，包含法官类型、诉讼策略等）
        String instruction = buildInstruction(currentRole, judgeType, userIdentity);
        requestBody.put("instruction", instruction);
        
        return requestBody;
    }
    
    /**
     * 将角色转换为中文
     */
    private String convertRoleToChinese(String role) {
        if (role == null) {
            return "审判员";
        }
        switch (role.toLowerCase()) {
            case "judge":
                return "审判员";
            case "plaintiff":
                return "原告";
            case "defendant":
                return "被告";
            default:
                return role;
        }
    }
    
    /**
     * 将消息列表转换为context格式（用\n分隔）
     * 格式：角色名: 内容\n角色名: 内容
     */
    private String convertMessagesToContext(List<Map<String, Object>> messages) {
        if (messages == null || messages.isEmpty()) {
            return "";
        }
        
        StringBuilder context = new StringBuilder();
        for (int i = 0; i < messages.size(); i++) {
            Map<String, Object> msg = messages.get(i);
            String name = (String) msg.get("name");
            Object textObj = msg.get("text");
            String text = textObj != null ? textObj.toString() : "";
            
            if (name != null && !text.isEmpty()) {
                if (context.length() > 0) {
                    context.append("\n");
                }
                context.append(name).append(": ").append(text);
            }
        }
        
        return context.toString();
    }
    
    /**
     * 构建instruction（角色指令）
     * 包含法官类型、诉讼策略等信息
     * 对于法官角色，法官类型会加入角色提示词中
     */
    private String buildInstruction(String currentRole, String judgeType, String userIdentity) {
        StringBuilder instruction = new StringBuilder();
        
        if ("judge".equalsIgnoreCase(currentRole)) {
            // 法官角色的instruction
            // 首先添加法官类型特征（这是最重要的，会直接影响法官的发言风格）
            if (judgeType != null && !judgeType.isEmpty()) {
                switch (judgeType) {
                    case "professional":
                        instruction.append("你是一位专业型法官，讲话简洁，业务熟练，判决果断。\n\n");
                        break;
                    case "strong":
                        instruction.append("你是一位强势型法官，专业能力出众，细节能力强。\n\n");
                        break;
                    case "partial-plaintiff":
                        instruction.append("你是一位偏袒型法官，习惯对原告宽容。\n\n");
                        break;
                    case "partial-defendant":
                        instruction.append("你是一位偏袒型法官，习惯对被告宽容。\n\n");
                        break;
                    case "neutral":
                    default:
                        instruction.append("你是一位中立型法官，保持中立，注重程序公正。\n\n");
                        break;
                }
            }
            
            // 然后添加法官职责
            instruction.append("作为审判员，你需要：\n");
            instruction.append("1. 保持中立、客观、公正的立场\n");
            instruction.append("2. 引导庭审程序有序进行，控制庭审节奏\n");
            instruction.append("3. 对争议焦点进行归纳和总结\n");
            instruction.append("4. 确保各方充分表达意见，维护庭审秩序\n");
            instruction.append("5. 基于事实和法律进行判断，不偏不倚\n");
            instruction.append("6. 在开庭时必须发言引导原告发言\n");
            instruction.append("7. 每发言一轮后，判断自己是否应该发言。如果发言，发言完应该决定下一个发言人的身份（原告或被告）\n");
            instruction.append("8. 如果不需要发言，由原告和被告方律师轮流发言");
        } else if ("plaintiff".equalsIgnoreCase(currentRole)) {
            // 原告角色的instruction
            instruction.append("作为原告代理律师，你需要：\n");
            instruction.append("1. 代表原告维护权益，提出诉讼请求\n");
            instruction.append("2. 提供证据和理由支持诉讼请求\n");
            instruction.append("3. 回应被告的答辩意见\n");
            instruction.append("4. 围绕争议焦点组织举证质证\n");
            instruction.append("5. 强调事实和法律依据\n\n");
            instruction.append("诉讼策略：均衡策略，主张明确，证据充分，但不过度激化矛盾。");
        } else if ("defendant".equalsIgnoreCase(currentRole)) {
            // 被告角色的instruction
            instruction.append("作为被告代理律师，你需要：\n");
            instruction.append("1. 代表被告进行辩护，反驳原告指控\n");
            instruction.append("2. 提出有利于被告的证据和事实\n");
            instruction.append("3. 质疑原告证据的合法性、真实性、关联性\n");
            instruction.append("4. 维护被告权益\n");
            instruction.append("5. 争取从轻、减轻或免除责任\n\n");
            instruction.append("诉讼策略：保守策略，优先考虑通过调解解决争议，可适当让步。");
        } else {
            // 默认instruction
            instruction.append("请根据你的角色定位，在法庭辩论中保持专业严谨。");
        }
        
        return instruction.toString();
    }
    
    /**
     * 检查AI服务健康状态
     */
    public boolean checkHealth() {
        try {
            String url = aiServiceUrl + "/health";
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            log.warn("AI服务健康检查失败", e);
            return false;
        }
    }
    
    /**
     * 初始化AI模型（后台异步加载）
     */
    public Map<String, Object> initModel() {
        try {
            String url = aiServiceUrl + "/api/model/init";
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(new HashMap<>(), headers);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return response.getBody();
            } else {
                throw new RuntimeException("模型初始化请求失败");
            }
        } catch (Exception e) {
            log.error("模型初始化失败", e);
            throw new RuntimeException("模型初始化失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 获取模型初始化状态
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getModelStatus() {
        try {
            String url = aiServiceUrl + "/api/model/status";
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                // AI服务返回格式: {"success": true, "status": {...}}
                // 我们需要提取status字段
                if (body.containsKey("status")) {
                    return (Map<String, Object>) body.get("status");
                }
                return body;
            } else {
                throw new RuntimeException("获取模型状态失败");
            }
        } catch (Exception e) {
            log.error("获取模型状态失败", e);
            throw new RuntimeException("获取模型状态失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 案件资料自动总结
     * 
     * @param fileNames 文件名列表
     * @param identity 用户身份（plaintiff 或 defendant）
     * @return AI生成的案件描述
     */
    public String summarizeCase(List<String> fileNames, String identity) {
        return summarizeCaseWithContent(fileNames, null, identity);
    }
    
    /**
     * 案件资料自动总结（带文件内容）
     * 
     * @param fileNames 文件名列表
     * @param fileContents 文件内容列表（可为null）
     * @param identity 用户身份（plaintiff 或 defendant）
     * @return AI生成的案件描述
     */
    public String summarizeCaseWithContent(List<String> fileNames, List<String> fileContents, String identity) {
        try {
            String url = aiServiceUrl + "/api/case/summarize";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("file_names", fileNames);
            if (fileContents != null && !fileContents.isEmpty()) {
                requestBody.put("file_contents", fileContents);
            }
            requestBody.put("identity", identity);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            // 输出详细的输入参数日志
            log.info("========== 调用AI服务：案件资料自动总结 ==========");
            log.info("URL: {}", url);
            log.info("用户身份: {}", identity);
            log.info("文件数量: {}", fileNames != null ? fileNames.size() : 0);
            if (fileNames != null && !fileNames.isEmpty()) {
                log.info("文件名列表:");
                for (int i = 0; i < fileNames.size(); i++) {
                    log.info("  [{}] {}", i + 1, fileNames.get(i));
                }
            }
            log.info("文件内容数量: {}", fileContents != null ? fileContents.size() : 0);
            if (fileContents != null && !fileContents.isEmpty()) {
                log.info("文件内容预览:");
                for (int i = 0; i < Math.min(3, fileContents.size()); i++) {
                    String content = fileContents.get(i);
                    log.info("  [{}] 内容长度: {} 字符", i + 1, content.length());
                    String preview = content.length() > 200 ? content.substring(0, 200) + "..." : content;
                    log.info("      预览: {}", preview);
                }
            }
            log.info("完整请求体: {}", objectMapper.writeValueAsString(requestBody));
            log.info("================================================");
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                Boolean success = (Boolean) body.get("success");
                if (Boolean.TRUE.equals(success)) {
                    String summary = (String) body.get("summary");
                    log.debug("案件总结生成成功，长度: {}", summary != null ? summary.length() : 0);
                    return summary;
                } else {
                    String error = (String) body.get("error");
                    log.error("案件总结API返回错误: {}", error);
                    throw new RuntimeException("案件总结失败: " + error);
                }
            } else {
                log.error("案件总结API调用失败，状态码: {}", response.getStatusCode());
                throw new RuntimeException("案件总结API调用失败");
            }
        } catch (Exception e) {
            log.error("调用案件总结API异常", e);
            throw new RuntimeException("案件总结失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 生成判决书
     * 
     * @param caseDescription 案件描述
     * @param messages 庭审对话历史
     * @param identity 用户身份
     * @return AI生成的判决书
     */
    public String generateVerdict(String caseDescription, List<Map<String, Object>> messages, String identity) {
        try {
            String url = aiServiceUrl + "/api/verdict/generate";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("case_description", caseDescription);
            requestBody.put("messages", messages);
            requestBody.put("identity", identity);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            // 输出详细的输入参数日志
            log.info("========== 调用AI服务：生成判决书 ==========");
            log.info("URL: {}", url);
            log.info("用户身份: {}", identity);
            log.info("案件描述长度: {} 字符", caseDescription != null ? caseDescription.length() : 0);
            if (caseDescription != null && !caseDescription.isEmpty()) {
                String descPreview = caseDescription.length() > 200 ? 
                    caseDescription.substring(0, 200) + "..." : caseDescription;
                log.info("案件描述预览: {}", descPreview);
            }
            log.info("庭审对话历史消息数: {}", messages != null ? messages.size() : 0);
            if (messages != null && !messages.isEmpty()) {
                log.info("对话历史预览（前5条）:");
                for (int i = 0; i < Math.min(5, messages.size()); i++) {
                    Map<String, Object> msg = messages.get(i);
                    Object textObj = msg.get("text");
                    String textPreview = "";
                    if (textObj != null) {
                        String text = textObj.toString();
                        if (text.length() > 150) {
                            textPreview = text.substring(0, 150) + "...";
                        } else {
                            textPreview = text;
                        }
                    }
                    log.info("  [{}] {}: {}", i + 1, msg.get("name"), textPreview);
                }
            }
            log.info("完整请求体: {}", objectMapper.writeValueAsString(requestBody));
            log.info("================================================");
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                Boolean success = (Boolean) body.get("success");
                if (Boolean.TRUE.equals(success)) {
                    String verdict = (String) body.get("verdict");
                    log.debug("判决书生成成功，长度: {}", verdict != null ? verdict.length() : 0);
                    return verdict;
                } else {
                    String error = (String) body.get("error");
                    log.error("判决书生成API返回错误: {}", error);
                    throw new RuntimeException("判决书生成失败: " + error);
                }
            } else {
                log.error("判决书生成API调用失败，状态码: {}", response.getStatusCode());
                throw new RuntimeException("判决书生成API调用失败");
            }
        } catch (Exception e) {
            log.error("调用判决书生成API异常", e);
            throw new RuntimeException("判决书生成失败: " + e.getMessage(), e);
        }
    }
}

