package com.mootai.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
public class DebateRequest {
    
    @NotBlank(message = "用户身份不能为空")
    private String userIdentity; // "plaintiff" 或 "defendant"
    
    @NotBlank(message = "当前角色不能为空")
    private String currentRole; // "judge", "plaintiff", "defendant"
    
    @NotNull(message = "对话历史不能为空")
    private List<Map<String, Object>> messages; // 对话历史
    
    private String judgeType = "neutral"; // 法官类型
    
    private String caseDescription = ""; // 案件描述
    
    private String opponentStrategy; // 对方AI律师的辩论策略（aggressive, conservative, balanced, defensive）
}


