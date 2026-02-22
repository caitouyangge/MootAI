package com.mootai.controller;

import com.mootai.dto.ApiResponse;
import com.mootai.dto.DebateRequest;
import com.mootai.service.AiService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/debate")
@RequiredArgsConstructor
public class DebateController {
    
    private final AiService aiService;
    
    /**
     * 生成法庭辩论回复
     */
    @PostMapping("/generate")
    public ApiResponse<String> generateDebateResponse(@Valid @RequestBody DebateRequest request) {
        try {
            String response = aiService.generateDebateResponse(
                request.getUserIdentity(),
                request.getCurrentRole(),
                request.getMessages(),
                request.getJudgeType(),
                request.getCaseDescription()
            );
            return ApiResponse.success("生成成功", response);
        } catch (Exception e) {
            return ApiResponse.error("生成失败: " + e.getMessage());
        }
    }
    
    /**
     * 检查AI服务健康状态
     */
    @GetMapping("/health")
    public ApiResponse<Boolean> checkHealth() {
        boolean isHealthy = aiService.checkHealth();
        return ApiResponse.success("检查完成", isHealthy);
    }
    
    /**
     * 初始化AI模型
     */
    @PostMapping("/model/init")
    public ApiResponse<Map<String, Object>> initModel() {
        try {
            Map<String, Object> result = aiService.initModel();
            return ApiResponse.success("模型初始化已启动", result);
        } catch (Exception e) {
            return ApiResponse.error("模型初始化失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取模型初始化状态
     */
    @GetMapping("/model/status")
    public ApiResponse<Map<String, Object>> getModelStatus() {
        try {
            Map<String, Object> status = aiService.getModelStatus();
            return ApiResponse.success("获取状态成功", status);
        } catch (Exception e) {
            return ApiResponse.error("获取模型状态失败: " + e.getMessage());
        }
    }
    
    /**
     * 生成判决书
     */
    @PostMapping("/verdict")
    public ApiResponse<String> generateVerdict(@RequestBody Map<String, Object> request) {
        try {
            String caseDescription = (String) request.get("caseDescription");
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> messages = (List<Map<String, Object>>) request.get("messages");
            String identity = (String) request.get("identity");
            
            if (caseDescription == null || caseDescription.isEmpty()) {
                return ApiResponse.error("案件描述不能为空");
            }
            
            String verdict = aiService.generateVerdict(caseDescription, messages, identity);
            return ApiResponse.success("判决书生成成功", verdict);
        } catch (Exception e) {
            return ApiResponse.error("判决书生成失败: " + e.getMessage());
        }
    }
}

