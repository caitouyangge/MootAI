package com.mootai.dto;

import lombok.Data;

import java.util.ArrayList;
import java.util.List;

@Data
public class CaseRequest {
    
    private String identity; // "plaintiff" 或 "defendant"（逐步保存时可能为空）
    
    private List<String> fileNames; // 文件名列表（逐步保存时可能为空）
    
    private String caseDescription; // 案件描述（逐步保存时可能为空）
    
    private String judgeType; // 审判员类型（可选）
    
    private String opponentStrategy; // 对方AI律师的辩论策略（可选）
    
    private String debateMessages; // 辩论消息（JSON格式，可选）
}

