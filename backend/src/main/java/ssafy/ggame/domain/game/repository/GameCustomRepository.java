package ssafy.ggame.domain.game.repository;

import ssafy.ggame.domain.game.dto.GameCardDto;
import ssafy.ggame.domain.game.dto.GameSaleCardDto;
import ssafy.ggame.domain.game.entity.Game;
import ssafy.ggame.domain.search.dto.SearchLikeRequestDto;
import ssafy.ggame.domain.topic.dto.SaleGameDto;

import java.util.List;
import java.util.Map;

public interface GameCustomRepository {
    // 게임명 검색 메소드
    List<GameCardDto> findByGameNameContaining(SearchLikeRequestDto dto);
    // 할인 게임 검색 메소드 ( 25, 50, 75 만 가져옴 )
    Map<Integer,List<GameSaleCardDto>> findSaleGames(Integer userId);
}