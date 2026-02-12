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
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("user_identity", userIdentity);
            requestBody.put("current_role", currentRole);
            requestBody.put("messages", messages);
            requestBody.put("judge_type", judgeType);
            requestBody.put("case_description", caseDescription);
            
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
            log.info("完整请求体: {}", objectMapper.writeValueAsString(requestBody));
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

