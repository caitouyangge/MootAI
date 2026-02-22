package com.mootai.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "cases")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Case {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "user_id", nullable = false)
    private Long userId;
    
    @Column(nullable = false, length = 20)
    private String identity; // "plaintiff" 或 "defendant"
    
    @Column(name = "case_description", columnDefinition = "TEXT")
    private String caseDescription;
    
    @ElementCollection
    @CollectionTable(name = "case_files", joinColumns = @JoinColumn(name = "case_id"))
    @Column(name = "file_name")
    private List<String> fileNames = new ArrayList<>();
    
    @Column(name = "judge_type", length = 50)
    private String judgeType; // 法官类型
    
    @Column(name = "opponent_strategy", length = 50)
    private String opponentStrategy; // 对方AI律师的辩论策略
    
    @Column(name = "debate_messages", columnDefinition = "TEXT")
    private String debateMessages; // 辩论消息（JSON格式存储）
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}

