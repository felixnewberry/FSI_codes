clear all
close all
clc

% Want to converge to C_D = 5.57 to 5.59, C_L 0.0104 to 0.0110, p_diff
% 0.1172 to 0.1176

% 32 has dofs_V 9888 and dofs_Q 1316
% 64 has dofs_V 37964 and dofs_Q 4908
% 128 is 147108, 18710. 
% 256 585792, 73868

% %load('results_64_vout.mat')
% load('results_32.mat')
% 
% p_diff_32 = results(:,1); 
% C_D_32 = results(:,2); 
% C_L_32 = -results(:,3); 
% t_vec_32 = linspace(0,8,length(C_L_32))'; 
% 
% load('results_64.mat')
% 
% p_diff_64 = results(1:end-1,1); 
% C_D_64 = results(1:end-1,2); 
% C_L_64 = results(1:end-1,3); 
% t_vec_64 = linspace(0,8,length(C_L_64))'; 
% 
% load('results_128.mat')
% p_diff_128 = results(:,1); 
% C_D_128 = results(:,2); 
% C_L_128 = -results(:,3); 
% t_vec_128 = linspace(0,8,length(C_L_128))'; 
% 
% load('results_256.mat')
% p_diff_256 = results(:,1); 
% C_D_256 = results(:,2); 
% C_L_256 = -results(:,3); 
% t_vec_256 = linspace(0,8,length(C_L_256))'; 
% 
% CD_l = 5.57; 
% CD_u = 5.59; 
% CL_l = 0.0104;
% CL_u = 0.0110; 
% p_diff_l = 0.1172;
% p_diff_u = 0.1176; 
% 
% figure
% hold on
% h1 = plot(t_vec_32, ones(1,length(t_vec_32))*CD_u,'-r', 'LineWidth', 2);
% h1 = plot(t_vec_32, ones(1,length(t_vec_32))*CD_l,'-r', 'LineWidth', 2);
% h2 = plot(t_vec_32,C_D_32,'-b', 'LineWidth', 2);
% h3 = plot(t_vec_64,C_D_64,'-g', 'LineWidth', 2);
% h4 = plot(t_vec_128,C_D_128,'-m', 'LineWidth', 2);
% h5 = plot(t_vec_256,C_D_256,'-c', 'LineWidth', 2);
% legend([h1,h2,h3,h4, h5], {'True', '32','64','128','256'},'interpreter', ...
%         'latex', 'fontsize', 16);
% hold off
% xlabel('time', 'interpreter', 'latex', 'fontsize', 20);
% ylabel('$C_D$', 'interpreter', 'latex', 'fontsize', 20);
% ylim([5, 5.7])
% % ylim([5, 13])
% 
% figure
% hold on
% h1 = plot(t_vec_32, ones(1,length(t_vec_32))*CL_u,'-r', 'LineWidth', 2);
% h1 = plot(t_vec_32, ones(1,length(t_vec_32))*CL_l,'-r', 'LineWidth', 2);
% h2 = plot(t_vec_32,C_L_32,'-b', 'LineWidth', 2);
% h3 = plot(t_vec_64,C_L_64,'-g', 'LineWidth', 2);
% h4 = plot(t_vec_128,C_L_128,'-m', 'LineWidth', 2);
% h5 = plot(t_vec_256,C_L_256,'-c', 'LineWidth', 2);
% legend([h1,h2,h3,h4, h5], {'True', '32','64','128','256'},'interpreter', ...
%         'latex', 'fontsize', 16);
% hold off
% xlabel('time', 'interpreter', 'latex', 'fontsize', 20);
% ylabel('$C_L$', 'interpreter', 'latex', 'fontsize', 20);
% ylim([0, 0.1])
% % ylim([0, 0.1])
% 
% figure
% hold on
% h1 = plot(t_vec_32, ones(1,length(t_vec_32))*p_diff_u,'-r', 'LineWidth', 2);
% h1 = plot(t_vec_32, ones(1,length(t_vec_32))*p_diff_l,'-r', 'LineWidth', 2);
% h2 = plot(t_vec_32,p_diff_32,'-b', 'LineWidth', 2);
% h3 = plot(t_vec_64,p_diff_64,'-g', 'LineWidth', 2);
% h4 = plot(t_vec_128,p_diff_128,'-m', 'LineWidth', 2);
% h5 = plot(t_vec_256,p_diff_256,'-c', 'LineWidth', 2);
% legend([h1,h2,h3,h4, h5], {'True', '32','64','128', '256'},'interpreter', ...
%         'latex', 'fontsize', 16);
% hold off
% xlabel('time', 'interpreter', 'latex', 'fontsize', 20)
% ylabel('$p_{diff}$', 'interpreter', 'latex', 'fontsize', 20)
% ylim([0.11, 0.135])

load('traction_tensor.mat')
% size is # points along FSI, measured quantities, t steps. 
% Columns are f_Traction_x,f_Traction_y,s_Traction_x,s_Traction_y
% where f is fluid traction force and s is structure

t_print = 9;

figure
hold on 
h1 = plot(traction_tensor(:,1,t_print), '-r', 'LineWidth', 2);
h2 = plot(-traction_tensor(:,3,t_print), '--b', 'LineWidth', 2);
legend([h1,h2], {'fluid','structure'},'interpreter', ...
        'latex', 'fontsize', 16);
hold off
xlabel('FSI nodal point', 'interpreter', 'latex', 'fontsize', 20)
ylabel('$F_{x}$', 'interpreter', 'latex', 'fontsize', 20)
% ylim([0.11, 0.135])

figure
hold on 
h1 = plot(traction_tensor(:,2,t_print), '-r', 'LineWidth', 2);
h2 = plot(-traction_tensor(:,4,t_print), '--b', 'LineWidth', 2);
legend([h1,h2], {'fluid','structure'},'interpreter', ...
        'latex', 'fontsize', 16);
hold off
xlabel('FSI nodal point', 'interpreter', 'latex', 'fontsize', 20)
ylabel('$F_{y}$', 'interpreter', 'latex', 'fontsize', 20)
% ylim([0.11, 0.135])

% does not seem crazy promising. 