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
     * @param judgeType 审判员类型
     * @param caseDescription 案件描述
     * @param opponentStrategy 对方AI律师的辩论策略（aggressive, conservative, balanced, defensive）
     * @return AI生成的回复
     */
    public String generateDebateResponse(
            String userIdentity,
            String currentRole,
            List<Map<String, Object>> messages,
            String judgeType,
            String caseDescription,
            String opponentStrategy
    ) {
        try {
            String url = aiServiceUrl + "/api/debate/generate";
            
            // 转换为训练数据格式
            Map<String, Object> requestBody = convertToTrainingFormat(
                    userIdentity, currentRole, messages, judgeType, caseDescription, opponentStrategy
            );
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(requestBody, headers);
            
            // 输出简化的日志（优化：减少日志输出以提升性能）
            log.debug("调用AI服务生成回复 - 角色: {}, 消息数: {}", currentRole, messages != null ? messages.size() : 0);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                Boolean success = (Boolean) body.get("success");
                Integer code = (Integer) body.get("code");
                
                // 检查success字段或code字段（兼容两种格式）
                if (Boolean.TRUE.equals(success) || (code != null && code == 200)) {
                    // Python AI服务返回格式: {"code": 200, "data": "...", "success": true}
                    // 优先从data字段获取，如果没有则从response字段获取（向后兼容）
                    String aiResponse = (String) body.get("data");
                    if (aiResponse == null) {
                        aiResponse = (String) body.get("response");
                    }
                    
                    if (aiResponse != null) {
                        log.debug("AI服务返回成功，长度: {}", aiResponse.length());
                        return aiResponse;
                    } else {
                        log.error("AI服务返回成功，但data和response字段都为空。响应体: {}", body);
                        throw new RuntimeException("AI服务返回格式错误：data字段为空");
                    }
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
     * @param judgeType 审判员类型
     * @param caseDescription 案件描述（现在包含完整的庭前准备资料）
     * @param opponentStrategy 对方AI律师的辩论策略
     * @return 训练数据格式的请求体
     */
    private Map<String, Object> convertToTrainingFormat(
            String userIdentity,
            String currentRole,
            List<Map<String, Object>> messages,
            String judgeType,
            String caseDescription,
            String opponentStrategy
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
        
        // 4. 转换 instruction（角色指令，包含审判员类型、诉讼策略等）
        String instruction = buildInstruction(currentRole, judgeType, userIdentity, opponentStrategy);
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
                return "公诉人";
            case "defendant":
                return "辩护人";
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
     * 包含审判员类型、诉讼策略等信息
     * 对于审判员角色，审判员类型会加入角色提示词中
     * 
     * @param currentRole 当前角色（judge, plaintiff, defendant）
     * @param judgeType 审判员类型
     * @param userIdentity 用户身份（plaintiff 或 defendant）
     * @param opponentStrategy 对方AI律师的辩论策略（aggressive, conservative, balanced, defensive）
     */
    private String buildInstruction(String currentRole, String judgeType, String userIdentity, String opponentStrategy) {
        StringBuilder instruction = new StringBuilder();
        
        if ("judge".equalsIgnoreCase(currentRole)) {
            // 审判员角色的instruction
            if (judgeType != null && !judgeType.isEmpty()) {
                switch (judgeType) {
                    case "professional":
                        instruction.append("专业型审判员：讲话简洁，业务熟练，判决果断。");
                        break;
                    case "strong":
                        instruction.append("强势型审判员：专业能力出众，细节能力强。");
                        break;
                    case "partial-plaintiff":
                        instruction.append("偏袒型审判员：习惯对公诉人宽容。");
                        break;
                    case "partial-defendant":
                        instruction.append("偏袒型审判员：习惯对辩护人宽容。");
                        break;
                    case "neutral":
                    default:
                        instruction.append("中立型审判员：保持中立，注重程序公正。");
                        break;
                }
                instruction.append("\n");
            }
            
            instruction.append("审判员职责：中立公正；引导程序；归纳焦点；维护秩序；基于事实与法律判断。");
            instruction.append("\n约束：禁止自指发言；对话历史非空时禁止重复\"现在开庭\"等开始语；不指定发言人（系统自动管理）；仅审判员/公诉人/辩护人可发言；结束语需完整（总结辩论、归纳焦点、说明情节、表明态度）。");
        } else if ("plaintiff".equalsIgnoreCase(currentRole)) {
            instruction.append("公诉人：行使公诉权；指控犯罪；举证质证；回应辩方；强调构成要件与量刑情节。");
            String strategy = getStrategyForRole("plaintiff", userIdentity, opponentStrategy);
            instruction.append("\n策略：").append(strategy);
        } else if ("defendant".equalsIgnoreCase(currentRole)) {
            instruction.append("辩护人：维护辩护人权益；提出辩护意见；提供有利证据；质疑控方证据；争取从轻减轻。");
            String strategy = getStrategyForRole("defendant", userIdentity, opponentStrategy);
            instruction.append("\n策略：").append(strategy);
        } else {
            instruction.append("保持专业严谨。");
        }
        
        return instruction.toString();
    }
    
    /**
     * 根据角色和用户身份获取策略
     * 
     * @param currentRole 当前角色（plaintiff 或 defendant）
     * @param userIdentity 用户身份（plaintiff 或 defendant）
     * @param opponentStrategy 对方AI律师的辩论策略
     * @return 策略描述
     */
    private String getStrategyForRole(String currentRole, String userIdentity, String opponentStrategy) {
        // 如果当前角色是用户自己，使用默认策略（均衡策略）
        if (currentRole.equalsIgnoreCase(userIdentity)) {
            return "均衡策略，主张明确，证据充分，但不过度激化矛盾。";
        }
        
        // 如果当前角色是对手，使用用户选择的对方策略
        if (opponentStrategy != null && !opponentStrategy.isEmpty()) {
            switch (opponentStrategy.toLowerCase()) {
                case "aggressive":
                    return "激进：强硬立场，积极进攻，不轻易让步，质疑对方证据，强调己方优势";
                case "conservative":
                    return "保守：优先调解，主张温和，可适当让步，避免激化矛盾";
                case "balanced":
                    return "均衡：主张适中，证据充分，不过度激化，保持协商空间";
                case "defensive":
                    return "防御：重点防守，回应质疑，保护核心利益，避免主动进攻";
                default:
                    return "均衡：主张适中，证据充分，不过度激化，保持协商空间";
            }
        }
        
        return "均衡：主张适中，证据充分，不过度激化，保持协商空间";
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

