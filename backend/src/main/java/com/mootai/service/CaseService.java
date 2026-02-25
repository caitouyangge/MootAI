package com.mootai.service;

import com.mootai.dto.CaseRequest;
import com.mootai.entity.Case;
import com.mootai.repository.CaseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class CaseService {
    
    private final CaseRepository caseRepository;
    
    @Transactional
    public Case createCase(Long userId, CaseRequest request) {
        Case caseEntity = new Case();
        caseEntity.setUserId(userId);
        
        // 设置字段，允许为空（逐步保存时可能部分字段为空）
        caseEntity.setIdentity(request.getIdentity() != null ? request.getIdentity() : "");
        caseEntity.setCaseDescription(request.getCaseDescription() != null ? request.getCaseDescription() : "");
        caseEntity.setFileNames(request.getFileNames() != null ? request.getFileNames() : new ArrayList<>());
        caseEntity.setJudgeType(request.getJudgeType());
        caseEntity.setOpponentStrategy(request.getOpponentStrategy());
        caseEntity.setDebateMessages(request.getDebateMessages());
        
        return caseRepository.save(caseEntity);
    }
    
    @Transactional
    public Case updateCase(Long caseId, Long userId, CaseRequest request) {
        Case caseEntity = caseRepository.findByIdAndUserId(caseId, userId);
        if (caseEntity == null) {
            throw new RuntimeException("案件不存在或无权限访问");
        }
        
        // 更新字段（允许空字符串，用于逐步保存）
        if (request.getIdentity() != null) {
            caseEntity.setIdentity(request.getIdentity());
        }
        if (request.getCaseDescription() != null) {
            caseEntity.setCaseDescription(request.getCaseDescription());
        }
        if (request.getFileNames() != null) {
            caseEntity.setFileNames(request.getFileNames());
        }
        // judgeType 和 opponentStrategy：如果前端发送了值（包括空字符串），则更新；如果为null，则不更新（保留原值）
        if (request.getJudgeType() != null) {
            caseEntity.setJudgeType(request.getJudgeType());
        }
        if (request.getOpponentStrategy() != null) {
            caseEntity.setOpponentStrategy(request.getOpponentStrategy());
        }
        // debateMessages 允许设置为 null（如果前端发送 null）
        if (request.getDebateMessages() != null) {
            caseEntity.setDebateMessages(request.getDebateMessages());
        }
        
        return caseRepository.save(caseEntity);
    }
    
    public List<Case> getUserCases(Long userId) {
        return caseRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }
    
    public Case getCaseById(Long caseId, Long userId) {
        return caseRepository.findByIdAndUserId(caseId, userId);
    }
}

